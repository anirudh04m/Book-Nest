from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# Book Models
class BookBase(BaseModel):
    isbn: str
    title: str
    publication_year: int
    publisher_id: int
    category_id: int

class Book(BookBase):
    class Config:
        from_attributes = True

class PublisherCreate(BaseModel):
    publisher_name: str
    publisher_city: Optional[str] = None

class Publisher(BaseModel):
    publisher_id: int
    publisher_name: str
    publisher_city: Optional[str] = None
    class Config:
        from_attributes = True

class BookCreate(BaseModel):
    isbn: str
    title: str
    publication_year: int
    publisher_id: int  # Back to publisher_id for dropdown
    category_id: int
    author_first_name: str
    author_last_name: str
    author_initials: Optional[str] = None
    author_role: str = "Author"
    price: Optional[float] = None
    can_rent: bool = False
    inventory_id: Optional[int] = 1

class BookDetail(BaseModel):
    isbn: str
    title: str
    author_name: str
    category_name: str
    publisher_name: str
    publication_year: int
    number_of_copies: int

# Customer Models
class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    customer_type: str
    phone_number: str
    zip_code: int

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    customer_id: int
    class Config:
        from_attributes = True

# Order Models
class OrderItemCreate(BaseModel):
    item_id: Optional[int] = None  # For non-book items
    isbn: Optional[str] = None  # For books
    quantity: int = 1

class OrderCreate(BaseModel):
    customer_id: int
    promotion_id: Optional[int] = None
    items: List[OrderItemCreate]

class OrderItem(BaseModel):
    order_item_id: int
    order_id: int
    item_id: int
    description: Optional[str] = None
    price: Optional[float] = None

class Order(BaseModel):
    order_id: int
    order_amount: float
    item_count: int
    order_date: date
    customer_id: int
    promotion_id: Optional[int] = None
    items: List[OrderItem] = []

# Item Models
class Item(BaseModel):
    item_id: int
    description: str
    price: float
    item_type: str

# Review Models
class ReviewCreate(BaseModel):
    content: str
    reviewer: str
    rating: float
    item_id: int

class Review(BaseModel):
    review_id: int
    content: str
    reviewer: str
    creation_date: datetime
    rating: float
    item_id: int

# BookRent Models
class BookRentCreate(BaseModel):
    customer_id: int
    b_item_id: Optional[int] = None  # For backward compatibility
    isbn: Optional[str] = None  # Preferred: use ISBN to auto-select available copy

class BookRent(BaseModel):
    book_rent_id: int
    rent_date: date
    due_date: date
    return_date: Optional[date] = None
    customer_id: int
    b_item_id: int

# Author Models
class Author(BaseModel):
    author_id: int
    author_first_name: str
    author_last_name: str
    initials: str

# Category Models
class Category(BaseModel):
    category_id: int
    category_name: str
    description: str

# Merchandise Models
class Merchandise(BaseModel):
    m_item_id: int
    item_id: int
    description: str
    price: float
    category_name: str

