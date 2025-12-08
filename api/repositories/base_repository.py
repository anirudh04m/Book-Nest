from typing import List, Optional, Dict, Any
from ..database import get_db_connection
from fastapi import HTTPException
import mysql.connector


class BaseRepository:
    """Base repository class with common database operations"""
    
    @staticmethod
    def execute_query(query: str, params: tuple = None, fetch: bool = True) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as a list of dictionaries.
        
        Args:
            query: SQL query string
            params: Optional tuple of parameters for parameterized queries
            fetch: Whether to fetch results (True) or just execute (False)
        
        Returns:
            List of dictionaries representing rows, or rowcount if fetch=False
        """
        conn = get_db_connection()
        # Use dictionary cursor to get results as dictionaries
        cursor = conn.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                results = cursor.fetchall()
                cursor.close()
                conn.close()
                return results
            else:
                conn.commit()
                rowcount = cursor.rowcount
                cursor.close()
                conn.close()
                return rowcount
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    def execute_transaction(operations: List[tuple]) -> Any:
        """
        Execute multiple operations in a single transaction.
        
        Args:
            operations: List of tuples (query, params) to execute
        
        Returns:
            Result from the last operation
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            results = []
            for query, params in operations:
                cursor.execute(query, params)
                if cursor.description:  # If query returns results
                    row = cursor.fetchone()
                    if row:
                        results.append(row)
            
            conn.commit()
            return results[-1] if results else None
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_connection():
        """Get a database connection for complex transactions"""
        return get_db_connection()

