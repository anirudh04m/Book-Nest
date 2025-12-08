from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository


class CustomerRepository(BaseRepository):
    """Repository for customer-related database operations"""
    
    @staticmethod
    def get_all_customers() -> List[Dict[str, Any]]:
        """Get all customers"""
        query = "SELECT * FROM Customer"
        return CustomerRepository.execute_query(query)
    
    @staticmethod
    def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
        """Get a single customer by ID"""
        query = "SELECT * FROM Customer WHERE customer_id = %s"
        results = CustomerRepository.execute_query(query, (customer_id,))
        return results[0] if results else None
    
    @staticmethod
    def create_customer(first_name: str, last_name: str, customer_type: str, 
                       phone_number: str, zip_code: int) -> Dict[str, Any]:
        """Create a new customer"""
        from ..database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            INSERT INTO Customer (first_name, last_name, customer_type, phone_number, zip_code)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (first_name, last_name, customer_type, phone_number, zip_code))
            customer_id = cursor.lastrowid
            conn.commit()
            
            # Get the newly created customer
            get_query = "SELECT * FROM Customer WHERE customer_id = %s"
            cursor.execute(get_query, (customer_id,))
            new_customer = cursor.fetchone()
            cursor.close()
            conn.close()
            return new_customer
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise

