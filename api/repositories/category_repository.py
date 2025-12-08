from typing import List, Dict, Any
from .base_repository import BaseRepository


class CategoryRepository(BaseRepository):
    """Repository for category-related database operations"""
    
    @staticmethod
    def get_all_categories() -> List[Dict[str, Any]]:
        """Get all categories"""
        query = "SELECT * FROM Category"
        return CategoryRepository.execute_query(query)

