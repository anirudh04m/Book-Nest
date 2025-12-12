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
                br.book_rent_id,
                br.rent_date,
                br.due_date,
                br.return_date,
                br.customer_id,
                br.b_item_id,
                COALESCE(b.title, i.description) AS book_title,
                COALESCE(b.isbn, bc.isbn) AS isbn,
                CONCAT(c.first_name, ' ', c.last_name) AS customer_name
            FROM BookRent br
            LEFT JOIN BookCopy bc ON br.b_item_id = bc.b_item_id
            LEFT JOIN Book b ON bc.isbn = b.isbn
            LEFT JOIN Item i ON br.b_item_id = i.item_id
            LEFT JOIN Customer c ON br.customer_id = c.customer_id
            WHERE br.customer_id = %s
            ORDER BY br.rent_date DESC
            """
            return BookRentRepository.execute_query(query, (customer_id,))
        query = """
        SELECT 
            br.book_rent_id,
            br.rent_date,
            br.due_date,
            br.return_date,
            br.customer_id,
            br.b_item_id,
            COALESCE(b.title, i.description) AS book_title,
            COALESCE(b.isbn, bc.isbn) AS isbn,
            CONCAT(c.first_name, ' ', c.last_name) AS customer_name
        FROM BookRent br
        LEFT JOIN BookCopy bc ON br.b_item_id = bc.b_item_id
        LEFT JOIN Book b ON bc.isbn = b.isbn
        LEFT JOIN Item i ON br.b_item_id = i.item_id
        LEFT JOIN Customer c ON br.customer_id = c.customer_id
        ORDER BY br.rent_date DESC
        """
        return BookRentRepository.execute_query(query)
    
    @staticmethod
    def create_rent(customer_id: int, isbn: str) -> Dict[str, Any]:
        """Create a new book rental by ISBN (automatically selects an available copy)"""
        from ..database import get_db_connection
        
        # Create rent record in a single transaction to avoid race conditions
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Find and lock an available, rentable copy in one query
            find_copy_query = """
            SELECT b_item_id, status, can_rent
            FROM BookCopy
            WHERE isbn = %s AND status = 'available' AND can_rent = 1
            LIMIT 1
            FOR UPDATE
            """
            cursor.execute(find_copy_query, (isbn,))
            copy_result = cursor.fetchone()
            
            if not copy_result:
                raise HTTPException(status_code=400, detail=f"No rentable copies available for ISBN {isbn}")
            
            b_item_id = copy_result['b_item_id']
            
            # Double-check status (should be available since we just selected it)
            if copy_result['status'] != 'available' or copy_result['can_rent'] != 1:
                raise HTTPException(status_code=400, detail="Book copy is not available for rent")
            
            # Create rent record
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

