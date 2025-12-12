from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from fastapi import HTTPException


class BookRentRepository(BaseRepository):
    """Repository for book rental-related database operations"""
    
    @staticmethod
    def get_all_rents(customer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all book rentals with book and customer details"""
        if customer_id:
            query = """
            SELECT 
                br.*,
                b.title AS book_title,
                b.isbn,
                CONCAT(c.first_name, ' ', c.last_name) AS customer_name
            FROM BookRent br
            JOIN BookCopy bc ON br.b_item_id = bc.b_item_id
            JOIN Book b ON bc.isbn = b.isbn
            JOIN Customer c ON br.customer_id = c.customer_id
            WHERE br.customer_id = %s
            ORDER BY br.rent_date DESC
            """
            return BookRentRepository.execute_query(query, (customer_id,))
        query = """
        SELECT 
            br.*,
            b.title AS book_title,
            b.isbn,
            CONCAT(c.first_name, ' ', c.last_name) AS customer_name
        FROM BookRent br
        JOIN BookCopy bc ON br.b_item_id = bc.b_item_id
        JOIN Book b ON bc.isbn = b.isbn
        JOIN Customer c ON br.customer_id = c.customer_id
        ORDER BY br.rent_date DESC
        """
        return BookRentRepository.execute_query(query)
    
    @staticmethod
    def create_rent(customer_id: int, isbn: str) -> Dict[str, Any]:
        """Create a new book rental by ISBN (automatically selects an available copy)"""
        from ..database import get_db_connection
        from .inventory_repository import InventoryRepository
        
        # Get an available copy for this ISBN
        available_copies = InventoryRepository.get_available_copies_by_isbn(isbn)
        rentable_copies = [copy for copy in available_copies if copy.get('can_rent', 0) == 1]
        
        if not rentable_copies:
            raise HTTPException(status_code=400, detail=f"No rentable copies available for ISBN {isbn}")
        
        # Use the first available copy
        b_item_id = rentable_copies[0]['b_item_id']
        
        # Create rent record
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Check if copy is available (with lock)
            check_status_query = "SELECT status FROM BookCopy WHERE b_item_id = %s FOR UPDATE"
            cursor.execute(check_status_query, (b_item_id,))
            copy_status = cursor.fetchone()
            if not copy_status or copy_status['status'] != 'available':
                raise HTTPException(status_code=400, detail="Book copy is not available for rent")
            
            insert_query = """
            INSERT INTO BookRent (customer_id, b_item_id, rent_date, due_date)
            VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 2 WEEK))
            """
            cursor.execute(insert_query, (customer_id, b_item_id))
            rent_id = cursor.lastrowid
            
            # Update BookCopy status to 'rented'
            update_status_query = "UPDATE BookCopy SET status = 'rented' WHERE b_item_id = %s"
            cursor.execute(update_status_query, (b_item_id,))
            
            conn.commit()
            
            # Get the newly created rent record with book details
            get_query = """
            SELECT 
                br.*,
                b.title AS book_title,
                b.isbn,
                CONCAT(c.first_name, ' ', c.last_name) AS customer_name
            FROM BookRent br
            JOIN BookCopy bc ON br.b_item_id = bc.b_item_id
            JOIN Book b ON bc.isbn = b.isbn
            JOIN Customer c ON br.customer_id = c.customer_id
            WHERE br.book_rent_id = %s
            """
            cursor.execute(get_query, (rent_id,))
            new_rent = cursor.fetchone()
            cursor.close()
            conn.close()
            return new_rent
        except HTTPException:
            conn.rollback()
            cursor.close()
            conn.close()
            raise
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise HTTPException(status_code=500, detail=f"Error creating rent: {str(e)}")
    
    @staticmethod
    def return_book(rent_id: int) -> Dict[str, Any]:
        """Mark a book as returned"""
        from ..database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Get the b_item_id before updating
            get_query = "SELECT b_item_id FROM BookRent WHERE book_rent_id = %s"
            cursor.execute(get_query, (rent_id,))
            rent_record = cursor.fetchone()
            if not rent_record:
                raise HTTPException(status_code=404, detail="Rent record not found")
            
            b_item_id = rent_record['b_item_id']
            
            # Update rent record
            query = """
            UPDATE BookRent 
            SET return_date = NOW()
            WHERE book_rent_id = %s
            """
            cursor.execute(query, (rent_id,))
            
            # Update BookCopy status back to 'available'
            update_status_query = "UPDATE BookCopy SET status = 'available' WHERE b_item_id = %s"
            cursor.execute(update_status_query, (b_item_id,))
            
            conn.commit()
            
            # Get the updated rent record
            get_query = "SELECT * FROM BookRent WHERE book_rent_id = %s"
            cursor.execute(get_query, (rent_id,))
            updated_rent = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not updated_rent:
                raise HTTPException(status_code=404, detail="Rent record not found")
            return updated_rent
        except HTTPException:
            raise
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise

