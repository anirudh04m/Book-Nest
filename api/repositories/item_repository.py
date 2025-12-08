from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository


class ItemRepository(BaseRepository):
    """Repository for item-related database operations"""
    
    @staticmethod
    def get_all_items(item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all items, optionally filtered by item_type"""
        if item_type:
            query = "SELECT * FROM Item WHERE item_type = %s"
            return ItemRepository.execute_query(query, (item_type,))
        query = "SELECT * FROM Item"
        return ItemRepository.execute_query(query)
    
    @staticmethod
    def get_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
        """Get a single item by ID"""
        query = "SELECT * FROM Item WHERE item_id = %s"
        results = ItemRepository.execute_query(query, (item_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_merchandise() -> List[Dict[str, Any]]:
        """Get all merchandise items"""
        query = """
        SELECT m.m_item_id as item_id, i.item_id, i.description, i.price, c.category_name
        FROM Merchandise m
        JOIN Item i ON m.m_item_id = i.item_id
        JOIN Category c ON m.category_id = c.category_id
        """
        return ItemRepository.execute_query(query)

