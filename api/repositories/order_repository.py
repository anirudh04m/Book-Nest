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
        """Get all items for a specific order"""
        query = """
        SELECT oi.*, i.description, i.price
        FROM OrderItem oi
        JOIN Item i ON oi.item_id = i.item_id
        WHERE oi.order_id = %s
        """
        return OrderRepository.execute_query(query, (order_id,))
    
    @staticmethod
    def create_order(customer_id: int, promotion_id: Optional[int], items: List[int]) -> Dict[str, Any]:
        """
        Create a new order with items.
        Uses a transaction to ensure data consistency.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Create order (MySQL doesn't support OUTPUT, use LAST_INSERT_ID instead)
            order_query = """
            INSERT INTO `Order` (customer_id, promotion_id, order_date, order_amount, item_count)
            VALUES (%s, %s, NOW(), 0, 0)
            """
            cursor.execute(order_query, (customer_id, promotion_id))
            new_order_id = cursor.lastrowid
            
            # Get the newly created order
            get_order_query = "SELECT * FROM `Order` WHERE order_id = %s"
            cursor.execute(get_order_query, (new_order_id,))
            new_order = cursor.fetchone()
            
            # Add order items and calculate total
            total_amount = 0
            for item_id in items:
                # Get item price
                item_query = "SELECT price FROM Item WHERE item_id = %s"
                cursor.execute(item_query, (item_id,))
                item_result = cursor.fetchone()
                if not item_result:
                    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
                item_price = item_result['price']
                total_amount += float(item_price)
                
                # Insert order item
                order_item_query = "INSERT INTO OrderItem (order_id, item_id) VALUES (%s, %s)"
                cursor.execute(order_item_query, (new_order_id, item_id))
            
            # Update order amount
            update_query = "UPDATE `Order` SET order_amount = %s, item_count = %s WHERE order_id = %s"
            cursor.execute(update_query, (total_amount, len(items), new_order_id))
            
            # Apply promotion if exists
            if promotion_id:
                promo_query = "SELECT discount_percent FROM Promotion WHERE promotion_id = %s"
                cursor.execute(promo_query, (promotion_id,))
                promo_result = cursor.fetchone()
                if promo_result:
                    discount = float(promo_result['discount_percent'])
                    discounted_amount = total_amount * (1 - discount / 100)
                    cursor.execute(update_query, (discounted_amount, len(items), new_order_id))
            
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

