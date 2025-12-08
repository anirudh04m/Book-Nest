from typing import List, Dict, Any
from .base_repository import BaseRepository


class AuthorRepository(BaseRepository):
    """Repository for author-related database operations"""
    
    @staticmethod
    def get_all_authors() -> List[Dict[str, Any]]:
        """Get all authors"""
        query = "SELECT * FROM Author"
        return AuthorRepository.execute_query(query)
    
    @staticmethod
    def search_authors(name: str) -> List[Dict[str, Any]]:
        """Search authors by first or last name"""
        query = """
        SELECT * FROM Author 
        WHERE author_first_name LIKE %s OR author_last_name LIKE %s
        """
        name_pattern = f"%{name}%"
        return AuthorRepository.execute_query(query, (name_pattern, name_pattern))

