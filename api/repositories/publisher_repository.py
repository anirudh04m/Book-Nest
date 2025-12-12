from typing import List, Dict, Any
from .base_repository import BaseRepository


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

