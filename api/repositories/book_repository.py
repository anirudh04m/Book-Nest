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
    
    @staticmethod
    def create_book(book_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new book with author, and optionally create Item and BookCopy.
        
        Args:
            book_data: Dictionary containing book information including:
                - isbn, title, publication_year, publisher_id, category_id
                - author_first_name, author_last_name, author_initials, author_role
                - price (optional), can_rent (optional), inventory_id (optional)
        
        Returns:
            Created book details
        """
        from ..database import get_db_connection
        from fastapi import HTTPException
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Check if book already exists
            check_query = "SELECT isbn FROM Book WHERE isbn = %s"
            cursor.execute(check_query, (book_data['isbn'],))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail=f"Book with ISBN {book_data['isbn']} already exists")
            
            # Find or create author
            author_query = """
            SELECT author_id FROM Author 
            WHERE author_first_name = %s AND author_last_name = %s
            """
            cursor.execute(author_query, (book_data['author_first_name'], book_data['author_last_name']))
            author_result = cursor.fetchone()
            
            if author_result:
                author_id = author_result['author_id']
            else:
                # Create new author
                initials = book_data.get('author_initials') or f"{book_data['author_first_name'][0]}.{book_data['author_last_name'][0]}."
                insert_author_query = """
                INSERT INTO Author (author_first_name, author_last_name, initials)
                VALUES (%s, %s, %s)
                """
                cursor.execute(insert_author_query, (
                    book_data['author_first_name'],
                    book_data['author_last_name'],
                    initials
                ))
                author_id = cursor.lastrowid
            
            # Create the book
            insert_book_query = """
            INSERT INTO Book (isbn, title, publication_year, publisher_id, category_id)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_book_query, (
                book_data['isbn'],
                book_data['title'],
                book_data['publication_year'],
                book_data['publisher_id'],
                book_data['category_id']
            ))
            
            # Link author to book in Wrote table
            wrote_query = """
            INSERT INTO Wrote (author_id, isbn, role)
            VALUES (%s, %s, %s)
            """
            cursor.execute(wrote_query, (
                author_id,
                book_data['isbn'],
                book_data.get('author_role', 'Author')
            ))
            
            # Optionally create Item and BookCopy if price is provided
            if book_data.get('price'):
                # Create Item
                insert_item_query = """
                INSERT INTO Item (description, price, item_type)
                VALUES (%s, %s, 'Book')
                """
                cursor.execute(insert_item_query, (book_data['title'], book_data['price']))
                item_id = cursor.lastrowid
                
                # Create BookCopy
                insert_bookcopy_query = """
                INSERT INTO BookCopy (b_item_id, isbn, inventory_id, can_rent)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_bookcopy_query, (
                    item_id,
                    book_data['isbn'],
                    book_data.get('inventory_id', 1),
                    1 if book_data.get('can_rent', False) else 0
                ))
            
            conn.commit()
            
            # Return the created book
            return BookRepository.get_book_by_isbn(book_data['isbn'])
            
        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating book: {str(e)}")
        finally:
            cursor.close()
            conn.close()

