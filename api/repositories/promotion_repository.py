from typing import List, Dict, Any
from datetime import date
from .base_repository import BaseRepository


class PromotionRepository(BaseRepository):
    """Repository for promotion-related database operations"""
    
    @staticmethod
    def get_all_promotions() -> List[Dict[str, Any]]:
        """Get all promotions"""
        try:
            query = "SELECT * FROM Promotion ORDER BY start_date DESC"
            return PromotionRepository.execute_query(query)
        except Exception:
            # Promotion table might not exist yet
            return []
    
    @staticmethod
    def get_active_promotions() -> List[Dict[str, Any]]:
        """Get currently active promotions"""
        try:
            query = """
            SELECT * FROM Promotion 
            WHERE start_date <= CURDATE() AND end_date >= CURDATE()
            ORDER BY discount_percent DESC
            """
            return PromotionRepository.execute_query(query)
        except Exception:
            # Promotion table might not exist yet
            return []
    
    @staticmethod
    def get_promotion_by_code(code: str) -> Dict[str, Any]:
        """Get promotion by code"""
        query = "SELECT * FROM Promotion WHERE code = %s"
        results = PromotionRepository.execute_query(query, (code,))
        return results[0] if results else None

