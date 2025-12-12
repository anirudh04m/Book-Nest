from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from ..database import get_db_connection
from fastapi import HTTPException


class InventoryRepository(BaseRepository):
    """Repository for inventory and book copy management"""
    
    @staticmethod
    def get_available_copies_by_isbn(isbn: str) -> List[Dict[str, Any]]:
        """Get all available book copies for a given ISBN"""
        query = """
        SELECT bc.*, i.description, i.price
        FROM BookCopy bc
        JOIN Item i ON bc.b_item_id = i.item_id
        WHERE bc.isbn = %s AND bc.status = 'available'
        """
        return InventoryRepository.execute_query(query, (isbn,))
    
    @staticmethod
    def get_available_count_by_isbn(isbn: str) -> int:
        """Get count of available copies for a given ISBN"""
        query = """
        SELECT COUNT(*) as count
        FROM BookCopy bc
        WHERE bc.isbn = %s AND bc.status = 'available'
        """
        results = InventoryRepository.execute_query(query, (isbn,))
        return results[0]['count'] if results else 0
    
    @staticmethod
    def reserve_copies(isbn: str, quantity: int) -> List[int]:
        """
        Reserve available book copies for an order.
        Returns list of b_item_ids that were reserved.
        Raises error if not enough copies available.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get available copies
            query = """
            SELECT b_item_id 
            FROM BookCopy 
            WHERE isbn = %s AND status = 'available'
            LIMIT %s
            FOR UPDATE
            """
            cursor.execute(query, (isbn, quantity))
            available_copies = cursor.fetchall()
            
            if len(available_copies) < quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Only {len(available_copies)} copies available, but {quantity} requested"
                )
            
            # Mark copies as sold
            item_ids = [copy['b_item_id'] for copy in available_copies]
            if item_ids:
                placeholders = ','.join(['%s'] * len(item_ids))
                update_query = f"""
                UPDATE BookCopy 
                SET status = 'sold' 
                WHERE b_item_id IN ({placeholders})
                """
                cursor.execute(update_query, tuple(item_ids))
            
            conn.commit()
            return item_ids
            
        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error reserving copies: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def add_book_copies(isbn: str, quantity: int, price: float, can_rent: bool = False) -> List[Dict[str, Any]]:
        """
        Add multiple copies of a book to inventory.
        Creates Item and BookCopy records for each copy.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get book title
            book_query = "SELECT title FROM Book WHERE isbn = %s"
            cursor.execute(book_query, (isbn,))
            book_result = cursor.fetchone()
            if not book_result:
                raise HTTPException(status_code=404, detail=f"Book with ISBN {isbn} not found")
            
            book_title = book_result['title']
            
            # Get or create inventory
            inventory_query = "SELECT inventory_id FROM Inventory LIMIT 1"
            cursor.execute(inventory_query)
            inventory_result = cursor.fetchone()
            
            if not inventory_result:
                # Create default inventory
                employee_query = "SELECT employee_id FROM Employee LIMIT 1"
                cursor.execute(employee_query)
                employee_result = cursor.fetchone()
                
                if not employee_result:
                    # Create default employee
                    cursor.execute("""
                        INSERT INTO Employee (emp_first_name, emp_last_name, start_date)
                        VALUES ('System', 'Admin', CURDATE())
                    """)
                    employee_id = cursor.lastrowid
                else:
                    employee_id = employee_result['employee_id']
                
                cursor.execute("INSERT INTO Inventory (employee_id) VALUES (%s)", (employee_id,))
                inventory_id = cursor.lastrowid
            else:
                inventory_id = inventory_result['inventory_id']
            
            created_copies = []
            
            # Create copies
            for i in range(quantity):
                # Create Item
                item_query = """
                INSERT INTO Item (description, price, item_type)
                VALUES (%s, %s, 'Book')
                """
                cursor.execute(item_query, (f"{book_title} - Copy {i+1}", price))
                item_id = cursor.lastrowid
                
                # Create BookCopy
                copy_query = """
                INSERT INTO BookCopy (b_item_id, isbn, inventory_id, can_rent, status)
                VALUES (%s, %s, %s, %s, 'available')
                """
                cursor.execute(copy_query, (item_id, isbn, inventory_id, 1 if can_rent else 0))
                
                created_copies.append({
                    'b_item_id': item_id,
                    'isbn': isbn,
                    'status': 'available'
                })
            
            conn.commit()
            return created_copies
            
        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error adding copies: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_inventory_summary(isbn: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get inventory summary by ISBN"""
        if isbn:
            query = """
            SELECT 
                b.isbn,
                b.title,
                COUNT(bc.b_item_id) as total_copies,
                SUM(CASE WHEN bc.status = 'available' THEN 1 ELSE 0 END) as available_copies,
                SUM(CASE WHEN bc.status = 'sold' THEN 1 ELSE 0 END) as sold_copies,
                SUM(CASE WHEN bc.status = 'rented' THEN 1 ELSE 0 END) as rented_copies
            FROM Book b
            LEFT JOIN BookCopy bc ON b.isbn = bc.isbn
            WHERE b.isbn = %s
            GROUP BY b.isbn, b.title
            """
            return InventoryRepository.execute_query(query, (isbn,))
        else:
            query = """
            SELECT 
                b.isbn,
                b.title,
                COUNT(bc.b_item_id) as total_copies,
                SUM(CASE WHEN bc.status = 'available' THEN 1 ELSE 0 END) as available_copies,
                SUM(CASE WHEN bc.status = 'sold' THEN 1 ELSE 0 END) as sold_copies,
                SUM(CASE WHEN bc.status = 'rented' THEN 1 ELSE 0 END) as rented_copies
            FROM Book b
            LEFT JOIN BookCopy bc ON b.isbn = bc.isbn
            GROUP BY b.isbn, b.title
            ORDER BY b.title
            """
            return InventoryRepository.execute_query(query)

