from typing import Dict, Any, List
from .base_repository import BaseRepository


class StatisticsRepository(BaseRepository):
    """Repository for statistics and analytics"""
    
    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        """Get dashboard statistics"""
        stats = {}
        
        # Total books
        books_query = "SELECT COUNT(DISTINCT isbn) as total FROM Book"
        books_result = StatisticsRepository.execute_query(books_query)
        stats['total_books'] = books_result[0]['total'] if books_result else 0
        
        # Total customers
        customers_query = "SELECT COUNT(*) as total FROM Customer"
        customers_result = StatisticsRepository.execute_query(customers_query)
        stats['total_customers'] = customers_result[0]['total'] if customers_result else 0
        
        # Total orders
        orders_query = "SELECT COUNT(*) as total FROM `Order`"
        orders_result = StatisticsRepository.execute_query(orders_query)
        stats['total_orders'] = orders_result[0]['total'] if orders_result else 0
        
        # Total revenue
        revenue_query = "SELECT COALESCE(SUM(order_amount), 0) as total FROM `Order`"
        revenue_result = StatisticsRepository.execute_query(revenue_query)
        stats['total_revenue'] = float(revenue_result[0]['total']) if revenue_result else 0.0
        
        # Active rentals
        rentals_query = "SELECT COUNT(*) as total FROM BookRent WHERE return_date IS NULL"
        rentals_result = StatisticsRepository.execute_query(rentals_query)
        stats['active_rentals'] = rentals_result[0]['total'] if rentals_result else 0
        
        # Total reviews
        reviews_query = "SELECT COUNT(*) as total FROM Review"
        reviews_result = StatisticsRepository.execute_query(reviews_query)
        stats['total_reviews'] = reviews_result[0]['total'] if reviews_result else 0
        
        return stats
    
    @staticmethod
    def get_popular_books(limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular books by rental count"""
        query = """
        SELECT 
            b.isbn,
            b.title,
            COUNT(br.book_rent_id) AS rental_count
        FROM Book b
        LEFT JOIN BookCopy bc ON b.isbn = bc.isbn
        LEFT JOIN BookRent br ON bc.b_item_id = br.b_item_id
        GROUP BY b.isbn, b.title
        ORDER BY rental_count DESC
        LIMIT %s
        """
        return StatisticsRepository.execute_query(query, (limit,))
    
    @staticmethod
    def get_recent_orders(limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent orders"""
        query = """
        SELECT 
            o.order_id,
            o.order_amount,
            o.order_date,
            CONCAT(c.first_name, ' ', c.last_name) AS customer_name
        FROM `Order` o
        JOIN Customer c ON o.customer_id = c.customer_id
        ORDER BY o.order_date DESC
        LIMIT %s
        """
        return StatisticsRepository.execute_query(query, (limit,))
    
    @staticmethod
    def get_revenue_by_month() -> List[Dict[str, Any]]:
        """Get revenue grouped by month"""
        query = """
        SELECT 
            DATE_FORMAT(order_date, '%Y-%m') AS month,
            COUNT(*) AS order_count,
            SUM(order_amount) AS total_revenue
        FROM `Order`
        GROUP BY DATE_FORMAT(order_date, '%Y-%m')
        ORDER BY month DESC
        LIMIT 12
        """
        return StatisticsRepository.execute_query(query)

