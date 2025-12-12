from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from ..database import get_db_connection
from fastapi import HTTPException
import mysql.connector


class OrderRepository(BaseRepository):
    """Repository for order-related database operations"""
    
    @staticmethod
    def get_all_orders() -> List[Dict[str, Any]]:
        """Get all orders with their items"""
        query = """
        SELECT o.*, 
               (SELECT COUNT(*) FROM OrderItem oi WHERE oi.order_id = o.order_id) as item_count
        FROM `Order` o
        ORDER BY o.order_date DESC
        """
        orders = OrderRepository.execute_query(query)
        for order in orders:
            order['items'] = OrderRepository.get_order_items(order['order_id'])
        return orders
    
    @staticmethod
    def get_order_by_id(order_id: int) -> Optional[Dict[str, Any]]:
        """Get a single order by ID with its items"""
        query = "SELECT * FROM `Order` WHERE order_id = %s"
        results = OrderRepository.execute_query(query, (order_id,))
        if not results:
            return None
        order = results[0]
        order['items'] = OrderRepository.get_order_items(order_id)
        return order
    
    @staticmethod
    def get_order_items(order_id: int) -> List[Dict[str, Any]]:
        """Get all items for a specific order, grouped by book ISBN"""
        query = """
        SELECT 
            oi.order_item_id,
            oi.order_id,
            oi.item_id,
            i.description,
            i.price,
            i.item_type,
            bc.isbn,
            b.title AS book_title
        FROM OrderItem oi
        JOIN Item i ON oi.item_id = i.item_id
        LEFT JOIN BookCopy bc ON oi.item_id = bc.b_item_id
        LEFT JOIN Book b ON bc.isbn = b.isbn
        WHERE oi.order_id = %s
        ORDER BY i.item_type, b.title, i.description
        """
        items = OrderRepository.execute_query(query, (order_id,))
        
        if not items:
            return []
        
        # Group books by ISBN and count quantities
        from collections import defaultdict
        grouped_items = []
        book_groups = defaultdict(lambda: {'quantity': 0, 'price': 0, 'title': '', 'isbn': ''})
        other_items = []
        
        for item in items:
            if item.get('item_type') == 'Book' and item.get('isbn'):
                isbn = item['isbn']
                book_groups[isbn]['quantity'] += 1
                book_groups[isbn]['price'] = float(item.get('price', 0))
                book_groups[isbn]['title'] = item.get('book_title') or item.get('description', 'Unknown Book')
                book_groups[isbn]['isbn'] = isbn
            else:
                # For non-book items, add quantity field and ensure order_id is present
                item_with_qty = dict(item)
                item_with_qty['quantity'] = 1
                if 'order_id' not in item_with_qty:
                    item_with_qty['order_id'] = order_id
                other_items.append(item_with_qty)
        
        # Add grouped books
        for isbn, group in book_groups.items():
            if group['quantity'] > 0:
                grouped_items.append({
                    'order_item_id': 0,  # Not applicable for grouped items
                    'order_id': order_id,  # Required field
                    'item_id': 0,
                    'description': f"{group['title']} (ISBN: {isbn})",
                    'price': group['price'],
                    'quantity': group['quantity'],
                    'item_type': 'Book',
                    'isbn': isbn
                })
        
        # Add other items
        grouped_items.extend(other_items)
        
        return grouped_items
    
    @staticmethod
    def create_order(customer_id: int, promotion_id: Optional[int], items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a new order with items.
        For books, uses ISBN + quantity. For other items, uses item_id.
        Uses a transaction to ensure data consistency.
        """
        from .inventory_repository import InventoryRepository
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            reserved_item_ids = []
            item_details = {}
            
            # Process each order item
            for item in items:
                if item.get('isbn'):
                    # Book order - use ISBN and quantity
                    isbn = item['isbn']
                    quantity = item.get('quantity', 1)
                    
                    # Check availability
                    available_count = InventoryRepository.get_available_count_by_isbn(isbn)
                    if available_count < quantity:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Not enough copies available for ISBN {isbn}. Available: {available_count}, Requested: {quantity}"
                        )
                    
                    # Reserve copies
                    reserved_b_item_ids = InventoryRepository.reserve_copies(isbn, quantity)
                    reserved_item_ids.extend(reserved_b_item_ids)
                    
                    # Get book details and prices for each reserved copy
                    if reserved_b_item_ids:
                        placeholders = ','.join(['%s'] * len(reserved_b_item_ids))
                        book_query = f"""
                        SELECT bc.b_item_id, b.title, i.price
                        FROM Book b
                        JOIN BookCopy bc ON b.isbn = bc.isbn
                        JOIN Item i ON bc.b_item_id = i.item_id
                        WHERE bc.b_item_id IN ({placeholders})
                        """
                        cursor.execute(book_query, tuple(reserved_b_item_ids))
                        book_results = cursor.fetchall()
                        
                        for book_result in book_results:
                            item_id = book_result['b_item_id']
                            item_details[item_id] = {
                                'price': float(book_result['price']),
                                'description': book_result['title'],
                                'item_type': 'Book'
                            }
                            
                elif item.get('item_id'):
                    # Non-book item
                    item_id = item['item_id']
                    quantity = item.get('quantity', 1)
                    
                    # Get item details
                    item_query = """
                    SELECT i.item_id, i.description, i.price, i.item_type
                    FROM Item i
                    WHERE i.item_id = %s
                    """
                    cursor.execute(item_query, (item_id,))
                    item_result = cursor.fetchone()
                    if not item_result:
                        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
                    
                    # Add item multiple times based on quantity
                    for _ in range(quantity):
                        reserved_item_ids.append(item_id)
                        item_details[item_id] = item_result
                else:
                    raise HTTPException(status_code=400, detail="Item must have either 'isbn' or 'item_id'")
            
            # Create order
            order_query = """
            INSERT INTO `Order` (customer_id, promotion_id, order_date, order_amount, item_count)
            VALUES (%s, %s, NOW(), 0, 0)
            """
            cursor.execute(order_query, (customer_id, promotion_id))
            new_order_id = cursor.lastrowid
            
            # Add order items and calculate total
            total_amount = 0
            for item_id in reserved_item_ids:
                # Get item detail (use cached details if available)
                if item_id in item_details:
                    item_detail = item_details[item_id]
                    item_price = float(item_detail.get('price', 0))
                else:
                    item_query = """
                    SELECT i.price, i.item_type
                    FROM Item i
                    WHERE i.item_id = %s
                    """
                    cursor.execute(item_query, (item_id,))
                    item_detail = cursor.fetchone()
                    
                    if not item_detail:
                        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
                    
                    item_price = float(item_detail['price'])
                    item_details[item_id] = item_detail
                
                total_amount += item_price
                
                # Insert order item
                order_item_query = "INSERT INTO OrderItem (order_id, item_id) VALUES (%s, %s)"
                cursor.execute(order_item_query, (new_order_id, item_id))
            
            # Update order amount
            update_query = "UPDATE `Order` SET order_amount = %s, item_count = %s WHERE order_id = %s"
            cursor.execute(update_query, (total_amount, len(reserved_item_ids), new_order_id))
            
            # Apply promotion if exists
            if promotion_id:
                promo_query = "SELECT discount_percent FROM Promotion WHERE promotion_id = %s"
                cursor.execute(promo_query, (promotion_id,))
                promo_result = cursor.fetchone()
                if promo_result:
                    discount = float(promo_result['discount_percent'])
                    discounted_amount = total_amount * (1 - discount / 100)
                    cursor.execute(update_query, (discounted_amount, len(reserved_item_ids), new_order_id))
            
            conn.commit()
            
            # Return full order with items
            return OrderRepository.get_order_by_id(new_order_id)
        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
            conn.close()

