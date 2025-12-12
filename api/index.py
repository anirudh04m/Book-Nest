from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
from .models import (
    Book, BookDetail, BookCreate, Publisher, PublisherCreate, Customer, CustomerCreate, Order, OrderCreate,
    OrderItem, Review, ReviewCreate, BookRent, BookRentCreate,
    Item, Author, Category, Merchandise
)
from .repositories.book_repository import BookRepository
from .repositories.customer_repository import CustomerRepository
from .repositories.order_repository import OrderRepository
from .repositories.review_repository import ReviewRepository
from .repositories.book_rent_repository import BookRentRepository
from .repositories.item_repository import ItemRepository
from .repositories.category_repository import CategoryRepository
from .repositories.author_repository import AuthorRepository
from .repositories.publisher_repository import PublisherRepository
from .repositories.statistics_repository import StatisticsRepository
from .repositories.promotion_repository import PromotionRepository
from .repositories.inventory_repository import InventoryRepository
from .database_init import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    try:
        initialize_database()
    except Exception as e:
        print(f"⚠️  Warning: Database initialization had issues: {e}")
        print("⚠️  Application will continue, but some features may not work.")
    yield
    # Cleanup code can go here if needed


app = FastAPI(
    docs_url="/api/py/docs",
    openapi_url="/api/py/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Books Endpoints
@app.get("/api/py/books", response_model=List[BookDetail])
def get_books():
    """Get all books with author, category, and publisher information"""
    return BookRepository.get_all_books()

@app.get("/api/py/books/for-ordering")
def get_books_for_ordering():
    """Get books with available copies for ordering"""
    return BookRepository.get_books_for_ordering()

@app.get("/api/py/books/for-renting")
def get_books_for_renting():
    """Get books with available copies for renting"""
    return BookRepository.get_books_for_renting()

@app.get("/api/py/books/{isbn}", response_model=BookDetail)
def get_book(isbn: str):
    """Get a single book by ISBN"""
    book = BookRepository.get_book_by_isbn(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.get("/api/py/books/{isbn}/copies")
def get_book_copies(isbn: str):
    """Get all copies of a book (not just available ones)"""
    return BookRepository.get_all_book_copies(isbn)

@app.get("/api/py/books/search/{keyword}")
def search_books(keyword: str):
    """Search books by title or author name"""
    return BookRepository.search_books(keyword)

@app.post("/api/py/books", response_model=BookDetail)
def create_book(book: BookCreate):
    """Create a new book with author information"""
    try:
        book_data = book.model_dump()
        new_book = BookRepository.create_book(book_data)
        if not new_book:
            raise HTTPException(status_code=500, detail="Failed to create book")
        return new_book
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating book: {str(e)}")

# Publishers Endpoints
@app.get("/api/py/publishers", response_model=List[Publisher])
def get_publishers():
    """Get all publishers"""
    return PublisherRepository.get_all_publishers()

@app.post("/api/py/publishers", response_model=Publisher)
def create_publisher(publisher: PublisherCreate):
    """Create a new publisher"""
    try:
        if not publisher.publisher_name or not publisher.publisher_name.strip():
            raise HTTPException(status_code=400, detail="Publisher name is required")
        
        new_publisher = PublisherRepository.create_publisher(
            publisher.publisher_name.strip(),
            publisher.publisher_city.strip() if publisher.publisher_city else None
        )
        
        if not new_publisher:
            raise HTTPException(status_code=500, detail="Failed to create publisher")
        
        return new_publisher
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"Error creating publisher: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating publisher: {error_detail}")

# Customers Endpoints
@app.get("/api/py/customers", response_model=List[Customer])
def get_customers():
    """Get all customers"""
    return CustomerRepository.get_all_customers()

@app.get("/api/py/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: int):
    """Get a single customer by ID"""
    customer = CustomerRepository.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.post("/api/py/customers", response_model=Customer)
def create_customer(customer: CustomerCreate):
    """Create a new customer"""
    new_customer = CustomerRepository.create_customer(
        customer.first_name,
        customer.last_name,
        customer.customer_type,
        customer.phone_number,
        customer.zip_code
    )
    if not new_customer:
        raise HTTPException(status_code=500, detail="Failed to create customer")
    return new_customer

# Orders Endpoints
@app.get("/api/py/orders", response_model=List[Order])
def get_orders():
    """Get all orders with their items"""
    return OrderRepository.get_all_orders()

@app.get("/api/py/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    """Get a single order by ID with its items"""
    order = OrderRepository.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/api/py/orders", response_model=Order)
def create_order(order: OrderCreate):
    """Create a new order with items"""
    # Convert Pydantic models to dicts for processing
    items_data = [item.model_dump() for item in order.items]
    new_order = OrderRepository.create_order(
        order.customer_id,
        order.promotion_id,
        items_data
    )
    if not new_order:
        raise HTTPException(status_code=500, detail="Failed to create order")
    return new_order

# Reviews Endpoints
@app.get("/api/py/reviews", response_model=List[Review])
def get_reviews(item_id: Optional[int] = None):
    """Get all reviews, optionally filtered by item_id"""
    return ReviewRepository.get_all_reviews(item_id)

@app.post("/api/py/reviews", response_model=Review)
def create_review(review: ReviewCreate):
    """Create a new review"""
    new_review = ReviewRepository.create_review(
        review.content,
        review.reviewer,
        review.rating,
        review.item_id
    )
    if not new_review:
        raise HTTPException(status_code=500, detail="Failed to create review")
    return new_review

# Book Rent Endpoints
@app.get("/api/py/book-rents", response_model=List[BookRent])
def get_book_rents(customer_id: Optional[int] = None):
    """Get all book rentals, optionally filtered by customer_id"""
    return BookRentRepository.get_all_rents(customer_id)

@app.post("/api/py/book-rents", response_model=dict)
def create_book_rent(rent: BookRentCreate):
    """Create a new book rental"""
    # Support both old format (b_item_id) and new format (isbn)
    if rent.isbn:
        rent_record = BookRentRepository.create_rent(rent.customer_id, rent.isbn)
    elif rent.b_item_id:
        # Fallback to old format for backward compatibility
        from ..database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT isbn FROM BookCopy WHERE b_item_id = %s", (rent.b_item_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if not result:
            raise HTTPException(status_code=404, detail="Book copy not found")
        rent_record = BookRentRepository.create_rent(rent.customer_id, result['isbn'])
    else:
        raise HTTPException(status_code=400, detail="Either 'isbn' or 'b_item_id' must be provided")
    return {"message": "Book rented successfully", "rent": rent_record}

@app.put("/api/py/book-rents/{rent_id}/return")
def return_book(rent_id: int):
    """Mark a book as returned"""
    rent_record = BookRentRepository.return_book(rent_id)
    return {"message": "Book returned successfully", "rent": rent_record}

# Categories Endpoints
@app.get("/api/py/categories", response_model=List[Category])
def get_categories():
    """Get all categories"""
    return CategoryRepository.get_all_categories()

# Authors Endpoints
@app.get("/api/py/authors", response_model=List[Author])
def get_authors():
    """Get all authors"""
    return AuthorRepository.get_all_authors()

@app.get("/api/py/authors/search/{name}")
def search_authors(name: str):
    """Search authors by first or last name"""
    return AuthorRepository.search_authors(name)

# Merchandise Endpoints
@app.get("/api/py/merchandise", response_model=List[Merchandise])
def get_merchandise():
    """Get all merchandise items"""
    return ItemRepository.get_merchandise()

# Items Endpoints
@app.get("/api/py/items", response_model=List[Item])
def get_items(item_type: Optional[str] = None):
    """Get all items, optionally filtered by item_type"""
    return ItemRepository.get_all_items(item_type)

@app.get("/api/py/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    """Get a single item by ID"""
    item = ItemRepository.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Statistics Endpoints
@app.get("/api/py/statistics/dashboard")
def get_dashboard_stats():
    """Get dashboard statistics"""
    return StatisticsRepository.get_dashboard_stats()

@app.get("/api/py/statistics/popular-books")
def get_popular_books(limit: int = 10):
    """Get most popular books"""
    return StatisticsRepository.get_popular_books(limit)

@app.get("/api/py/statistics/recent-orders")
def get_recent_orders(limit: int = 10):
    """Get recent orders"""
    return StatisticsRepository.get_recent_orders(limit)

@app.get("/api/py/statistics/revenue-by-month")
def get_revenue_by_month():
    """Get revenue grouped by month"""
    return StatisticsRepository.get_revenue_by_month()

# Promotions Endpoints
@app.get("/api/py/promotions")
def get_promotions():
    """Get all active promotions"""
    from .repositories.promotion_repository import PromotionRepository
    return PromotionRepository.get_active_promotions()

@app.get("/api/py/promotions/all")
def get_all_promotions():
    """Get all promotions"""
    from .repositories.promotion_repository import PromotionRepository
    return PromotionRepository.get_all_promotions()

# Inventory Endpoints
@app.get("/api/py/inventory")
def get_inventory_summary(isbn: Optional[str] = None):
    """Get inventory summary, optionally filtered by ISBN"""
    return InventoryRepository.get_inventory_summary(isbn)

@app.get("/api/py/inventory/{isbn}/available")
def get_available_count(isbn: str):
    """Get available copy count for a book"""
    count = InventoryRepository.get_available_count_by_isbn(isbn)
    return {"isbn": isbn, "available_count": count}

@app.post("/api/py/inventory/{isbn}/add-copies")
def add_book_copies(isbn: str, quantity: int, price: float, can_rent: bool = False):
    """Add multiple copies of a book to inventory"""
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    if price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than 0")
    copies = InventoryRepository.add_book_copies(isbn, quantity, price, can_rent)
    return {"message": f"Added {quantity} copies", "copies": copies}

@app.post("/api/py/database/init")
def init_database():
    """Manually initialize database and tables"""
    try:
        initialize_database()
        return {"message": "Database initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")

@app.get("/api/py/helloFastApi")
def hello_fast_api():
    return {"message": "Hello from FastAPI"}
