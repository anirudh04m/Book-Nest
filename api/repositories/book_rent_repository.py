from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from fastapi import HTTPException


class BookRentRepository(BaseRepository):
    """Repository for book rental-related database operations"""
    
    @staticmethod
    def get_all_rents(customer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all book rentals, optionally filtered by customer_id"""
        if customer_id:
            query = "SELECT * FROM BookRent WHERE customer_id = %s ORDER BY rent_date DESC"
            return BookRentRepository.execute_query(query, (customer_id,))
        query = "SELECT * FROM BookRent ORDER BY rent_date DESC"
        return BookRentRepository.execute_query(query)
    
    @staticmethod
    def create_rent(customer_id: int, b_item_id: int) -> Dict[str, Any]:
        """Create a new book rental"""
        from ..database import get_db_connection
        # Check if book is available for rent
        check_query = "SELECT can_rent FROM BookCopy WHERE b_item_id = %s"
        results = BookRentRepository.execute_query(check_query, (b_item_id,))
        if not results or not results[0]['can_rent']:
            raise HTTPException(status_code=400, detail="Book cannot be rented")
        
        # Check if book is currently rented
        status_query = """
        SELECT return_date FROM BookRent 
        WHERE b_item_id = %s 
        ORDER BY rent_date DESC
        LIMIT 1
        """
        rent_status = BookRentRepository.execute_query(status_query, (b_item_id,))
        if rent_status and rent_status[0]['return_date'] is None:
            raise HTTPException(status_code=400, detail="Book is currently rented")
        
        # Create rent record
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            insert_query = """
            INSERT INTO BookRent (customer_id, b_item_id, rent_date, due_date)
            VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 2 WEEK))
            """
            cursor.execute(insert_query, (customer_id, b_item_id))
            rent_id = cursor.lastrowid
            conn.commit()
            
            # Get the newly created rent record
            get_query = "SELECT * FROM BookRent WHERE book_rent_id = %s"
            cursor.execute(get_query, (rent_id,))
            new_rent = cursor.fetchone()
            cursor.close()
            conn.close()
            return new_rent
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise
    
    @staticmethod
    def return_book(rent_id: int) -> Dict[str, Any]:
        """Mark a book as returned"""
        from ..database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            UPDATE BookRent 
            SET return_date = NOW()
            WHERE book_rent_id = %s
            """
            cursor.execute(query, (rent_id,))
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

