from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from ..database import get_db_connection


class PublisherRepository(BaseRepository):
    """Repository for publisher-related database operations"""
    
    @staticmethod
    def get_all_publishers() -> List[Dict[str, Any]]:
        """Get all publishers"""
        query = "SELECT * FROM Publisher"
        return PublisherRepository.execute_query(query)
    
    @staticmethod
    def get_publisher_by_id(publisher_id: int) -> Dict[str, Any]:
        """Get a single publisher by ID"""
        query = "SELECT * FROM Publisher WHERE publisher_id = %s"
        results = PublisherRepository.execute_query(query, (publisher_id,))
        return results[0] if results else None
    
    @staticmethod
    def create_publisher(publisher_name: str, publisher_city: Optional[str] = None) -> Dict[str, Any]:
        """Create a new publisher"""
        from ..database import get_db_connection
        from fastapi import HTTPException
        
        if not publisher_name or not publisher_name.strip():
            raise HTTPException(status_code=400, detail="Publisher name cannot be empty")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Check if publisher already exists
            check_query = "SELECT * FROM Publisher WHERE publisher_name = %s"
            cursor.execute(check_query, (publisher_name.strip(),))
            existing = cursor.fetchone()
            if existing:
                cursor.close()
                conn.close()
                return existing
            
            # Create new publisher
            insert_query = """
            INSERT INTO Publisher (publisher_name, publisher_city)
            VALUES (%s, %s)
            """
            city_value = publisher_city.strip() if publisher_city and publisher_city.strip() else None
            cursor.execute(insert_query, (publisher_name.strip(), city_value))
            publisher_id = cursor.lastrowid
            conn.commit()
            
            if not publisher_id:
                raise HTTPException(status_code=500, detail="Failed to get publisher ID after creation")
            
            # Get the newly created publisher
            get_query = "SELECT * FROM Publisher WHERE publisher_id = %s"
            cursor.execute(get_query, (publisher_id,))
            new_publisher = cursor.fetchone()
            
            if not new_publisher:
                raise HTTPException(status_code=500, detail="Failed to retrieve created publisher")
            
            cursor.close()
            conn.close()
            return new_publisher
        except HTTPException:
            if conn:
                conn.rollback()
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    @staticmethod
    def find_or_create_publisher(publisher_name: str, publisher_city: Optional[str] = None) -> int:
        """
        Find a publisher by name, or create it if it doesn't exist.
        Returns the publisher_id.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Try to find existing publisher
            find_query = "SELECT publisher_id FROM Publisher WHERE publisher_name = %s"
            cursor.execute(find_query, (publisher_name,))
            result = cursor.fetchone()
            
            if result:
                publisher_id = result['publisher_id']
            else:
                # Create new publisher
                insert_query = """
                INSERT INTO Publisher (publisher_name, publisher_city)
                VALUES (%s, %s)
                """
                cursor.execute(insert_query, (publisher_name, publisher_city or ''))
                publisher_id = cursor.lastrowid
                conn.commit()
            
            cursor.close()
            conn.close()
            return publisher_id
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise

