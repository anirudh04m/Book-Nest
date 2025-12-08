from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository


class ReviewRepository(BaseRepository):
    """Repository for review-related database operations"""
    
    @staticmethod
    def get_all_reviews(item_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all reviews, optionally filtered by item_id"""
        if item_id:
            query = "SELECT * FROM Review WHERE item_id = %s ORDER BY creation_date DESC"
            return ReviewRepository.execute_query(query, (item_id,))
        query = "SELECT * FROM Review ORDER BY creation_date DESC"
        return ReviewRepository.execute_query(query)
    
    @staticmethod
    def create_review(content: str, reviewer: str, rating: float, item_id: int) -> Dict[str, Any]:
        """Create a new review"""
        from ..database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            INSERT INTO Review (content, reviewer, creation_date, rating, item_id)
            VALUES (%s, %s, NOW(), %s, %s)
            """
            cursor.execute(query, (content, reviewer, rating, item_id))
            review_id = cursor.lastrowid
            conn.commit()
            
            # Get the newly created review
            get_query = "SELECT * FROM Review WHERE review_id = %s"
            cursor.execute(get_query, (review_id,))
            new_review = cursor.fetchone()
            cursor.close()
            conn.close()
            return new_review
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise

