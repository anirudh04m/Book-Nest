from typing import List, Dict, Any
from .base_repository import BaseRepository


class BookRepository(BaseRepository):
    """Repository for book-related database operations"""
    
    @staticmethod
    def get_all_books() -> List[Dict[str, Any]]:
        """Get all books with author, category, and publisher information"""
        query = """
        SELECT 
            b.isbn, 
            b.title, 
            CONCAT(a.author_first_name, ' ', a.author_last_name) AS author_name,
            cat.category_name,
            pub.publisher_name,
            b.publication_year,
            COUNT(bc.b_item_id) AS number_of_copies
        FROM 
            Book b
            JOIN Publisher pub ON b.publisher_id = pub.publisher_id
            JOIN Category cat ON b.category_id = cat.category_id
            JOIN Wrote w ON b.isbn = w.isbn
            JOIN Author a ON w.author_id = a.author_id
            LEFT JOIN BookCopy bc ON b.isbn = bc.isbn
        GROUP BY 
            b.isbn, b.title, a.author_first_name, a.author_last_name, 
            cat.category_name, pub.publisher_name, b.publication_year
        """
        return BookRepository.execute_query(query)
    
    @staticmethod
    def get_book_by_isbn(isbn: str) -> Dict[str, Any]:
        """Get a single book by ISBN"""
        query = """
        SELECT 
            b.isbn, 
            b.title, 
            CONCAT(a.author_first_name, ' ', a.author_last_name) AS author_name,
            cat.category_name,
            pub.publisher_name,
            b.publication_year,
            COUNT(bc.b_item_id) AS number_of_copies
        FROM 
            Book b
            JOIN Publisher pub ON b.publisher_id = pub.publisher_id
            JOIN Category cat ON b.category_id = cat.category_id
            JOIN Wrote w ON b.isbn = w.isbn
            JOIN Author a ON w.author_id = a.author_id
            LEFT JOIN BookCopy bc ON b.isbn = bc.isbn
        WHERE b.isbn = %s
        GROUP BY 
            b.isbn, b.title, a.author_first_name, a.author_last_name, 
            cat.category_name, pub.publisher_name, b.publication_year
        """
        results = BookRepository.execute_query(query, (isbn,))
        return results[0] if results else None
    
    @staticmethod
    def search_books(keyword: str) -> List[Dict[str, Any]]:
        """Search books by title or author name"""
        query = """
        SELECT DISTINCT
            b.isbn,
            b.title,
            CONCAT(a.author_first_name, ' ', a.author_last_name) AS author_name,
            cat.category_name,
            i.price
        FROM Book b
        JOIN Wrote w ON b.isbn = w.isbn
        JOIN Author a ON w.author_id = a.author_id
        JOIN Category cat ON b.category_id = cat.category_id
        JOIN BookCopy bc ON b.isbn = bc.isbn
        JOIN Item i ON bc.b_item_id = i.item_id
        WHERE b.title LIKE %s OR a.author_first_name LIKE %s OR a.author_last_name LIKE %s
        """
        keyword_pattern = f"%{keyword}%"
        return BookRepository.execute_query(query, (keyword_pattern, keyword_pattern, keyword_pattern))

