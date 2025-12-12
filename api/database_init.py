"""
Database initialization script.
Creates database and all required tables if they don't exist.
Converts SQL Server syntax to MySQL syntax.
"""
import mysql.connector
from mysql.connector import Error
from .database import DATABASE_CONFIG, get_db_connection


def get_connection_without_db():
    """Get connection without specifying database (to create it if needed)"""
    config = DATABASE_CONFIG.copy()
    database_name = config.pop("database")
    try:
        conn = mysql.connector.connect(**config)
        return conn, database_name
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise


def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    try:
        conn, db_name = get_connection_without_db()
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{db_name}' ready")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"❌ Error creating database: {e}")
        raise


def table_exists(table_name: str) -> bool:
    """Check if a table exists"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        db_name = DATABASE_CONFIG['database']
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_name = %s
        """, (db_name, table_name))
        result = cursor.fetchone()
        exists = result[0] > 0
        cursor.close()
        conn.close()
        return exists
    except Error as e:
        print(f"Error checking table {table_name}: {e}")
        return False


def initialize_tables():
    """Create all tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Category table
        if not table_exists("Category"):
            cursor.execute("""
                CREATE TABLE Category (
                    category_id INT AUTO_INCREMENT PRIMARY KEY,
                    category_name VARCHAR(255) NOT NULL,
                    description VARCHAR(255) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Category table")
        
        # Author table
        if not table_exists("Author"):
            cursor.execute("""
                CREATE TABLE Author (
                    author_id INT AUTO_INCREMENT PRIMARY KEY,
                    author_first_name VARCHAR(50) NOT NULL,
                    author_last_name VARCHAR(50) NOT NULL,
                    initials CHAR(10) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Author table")
        
        # Publisher table
        if not table_exists("Publisher"):
            cursor.execute("""
                CREATE TABLE Publisher (
                    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
                    publisher_name VARCHAR(255),
                    publisher_city VARCHAR(255)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Publisher table")
        
        # Employee table
        if not table_exists("Employee"):
            cursor.execute("""
                CREATE TABLE Employee (
                    employee_id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_first_name VARCHAR(255),
                    emp_last_name VARCHAR(255),
                    date_of_birth DATE,
                    start_date DATE,
                    salary DECIMAL(10, 2),
                    schedule_time VARCHAR(255)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Employee table")
        
        # Inventory table
        if not table_exists("Inventory"):
            cursor.execute("""
                CREATE TABLE Inventory (
                    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_id INT NOT NULL,
                    CONSTRAINT Inventory_FK FOREIGN KEY(employee_id) REFERENCES Employee(employee_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Inventory table")
        
        # Promotion table
        if not table_exists("Promotion"):
            cursor.execute("""
                CREATE TABLE Promotion (
                    promotion_id INT AUTO_INCREMENT PRIMARY KEY,
                    code VARCHAR(255),
                    description VARCHAR(255),
                    discount_percent DECIMAL(5, 2),
                    start_date DATE DEFAULT (CURRENT_DATE),
                    end_date DATE DEFAULT (CURRENT_DATE)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Promotion table")
        
        # Location table
        if not table_exists("Location"):
            cursor.execute("""
                CREATE TABLE Location (
                    zip_code INT NOT NULL,
                    city VARCHAR(20),
                    state CHAR(2),
                    CONSTRAINT Location_PK PRIMARY KEY (zip_code),
                    CONSTRAINT Zipcode_CK CHECK (zip_code BETWEEN 500 AND 99999)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Location table")
        
        # Customer table
        if not table_exists("Customer"):
            cursor.execute("""
                CREATE TABLE Customer (
                    customer_id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(25),
                    last_name VARCHAR(25),
                    customer_type VARCHAR(50),
                    phone_number CHAR(15),
                    zip_code INT NOT NULL,
                    CONSTRAINT Customer_FK FOREIGN KEY (zip_code) REFERENCES Location(zip_code),
                    CONSTRAINT PhoneNumber_CK CHECK (phone_number REGEXP '^[0-9]{3}-[0-9]{3}-[0-9]{4}$'),
                    CONSTRAINT Uc_PhoneNumber UNIQUE(phone_number)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Customer table")
        
        # Book table
        if not table_exists("Book"):
            cursor.execute("""
                CREATE TABLE Book (
                    isbn VARCHAR(20) PRIMARY KEY,
                    title VARCHAR(255),
                    publication_year INT,
                    publisher_id INT NOT NULL,
                    category_id INT NOT NULL,
                    FOREIGN KEY (publisher_id) REFERENCES Publisher(publisher_id),
                    FOREIGN KEY (category_id) REFERENCES Category(category_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Book table")
        
        # Item table
        if not table_exists("Item"):
            cursor.execute("""
                CREATE TABLE Item (
                    item_id INT AUTO_INCREMENT PRIMARY KEY,
                    description VARCHAR(255) NOT NULL,
                    price DECIMAL(6,2) NOT NULL,
                    item_type VARCHAR(20) NOT NULL,
                    CONSTRAINT item_price_nonnegative_CK CHECK (price >= 0),
                    CONSTRAINT item_type_chk CHECK (item_type IN ('Book', 'Merchandise'))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Item table")
        
        # Merchandise table
        if not table_exists("Merchandise"):
            cursor.execute("""
                CREATE TABLE Merchandise (
                    m_item_id INT NOT NULL PRIMARY KEY,
                    inventory_id INT NOT NULL,
                    category_id INT NOT NULL,
                    CONSTRAINT merchandise_fk1 FOREIGN KEY (m_item_id) REFERENCES Item(item_id),
                    CONSTRAINT merchandise_fk2 FOREIGN KEY (inventory_id) REFERENCES Inventory(inventory_id),
                    CONSTRAINT merchandise_fk3 FOREIGN KEY (category_id) REFERENCES Category(category_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Merchandise table")
        
        # Review table
        if not table_exists("Review"):
            cursor.execute("""
                CREATE TABLE Review (
                    review_id INT AUTO_INCREMENT PRIMARY KEY,
                    content VARCHAR(255),
                    reviewer VARCHAR(50) NOT NULL,
                    creation_date DATETIME NOT NULL,
                    rating DECIMAL(3,2) NOT NULL,
                    item_id INT NOT NULL,
                    CONSTRAINT Review_FK FOREIGN KEY(item_id) REFERENCES Item(item_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Review table")
        
        # Order table (using backticks because Order is a reserved word)
        if not table_exists("Order"):
            cursor.execute("""
                CREATE TABLE `Order` (
                    order_id INT AUTO_INCREMENT PRIMARY KEY,
                    order_amount DECIMAL(6,2),
                    item_count INT NOT NULL DEFAULT 0,
                    order_date DATE DEFAULT (CURRENT_DATE),
                    customer_id INT NOT NULL,
                    promotion_id INT,
                    CONSTRAINT Order_FK1 FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
                    CONSTRAINT Order_FK2 FOREIGN KEY (promotion_id) REFERENCES Promotion(promotion_id),
                    CONSTRAINT Order_amount_nonnegative_CK CHECK (order_amount >= 0)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Order table")
        
        # OrderItem table
        if not table_exists("OrderItem"):
            cursor.execute("""
                CREATE TABLE OrderItem (
                    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT NOT NULL,
                    item_id INT NOT NULL,
                    CONSTRAINT OrderItem_FK1 FOREIGN KEY (order_id) REFERENCES `Order`(order_id),
                    CONSTRAINT OrderItem_FK2 FOREIGN KEY (item_id) REFERENCES Item(item_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created OrderItem table")
        
        # BookCopy table
        if not table_exists("BookCopy"):
            cursor.execute("""
                CREATE TABLE BookCopy (
                    b_item_id INT PRIMARY KEY,
                    isbn VARCHAR(20),
                    inventory_id INT,
                    can_rent BOOLEAN,
                    status ENUM('available', 'sold', 'rented') DEFAULT 'available',
                    FOREIGN KEY (isbn) REFERENCES Book(isbn),
                    FOREIGN KEY (b_item_id) REFERENCES Item(item_id),
                    FOREIGN KEY (inventory_id) REFERENCES Inventory(inventory_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created BookCopy table")
        else:
            # Add status column if table exists but column doesn't
            try:
                cursor.execute("ALTER TABLE BookCopy ADD COLUMN status ENUM('available', 'sold', 'rented') DEFAULT 'available'")
                print("✅ Added status column to BookCopy table")
            except Exception:
                # Column might already exist
                pass
        
        # BookRent table
        if not table_exists("BookRent"):
            cursor.execute("""
                CREATE TABLE BookRent (
                    book_rent_id INT AUTO_INCREMENT PRIMARY KEY,
                    rent_date DATE DEFAULT (CURRENT_DATE),
                    due_date DATE,
                    return_date DATE,
                    customer_id INT NOT NULL,
                    b_item_id INT NOT NULL,
                    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
                    FOREIGN KEY (b_item_id) REFERENCES BookCopy(b_item_id),
                    CONSTRAINT CHK_ReturnDateGreaterThanRentDate CHECK (return_date IS NULL OR return_date > rent_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created BookRent table")
        
        # Penalty table
        if not table_exists("Penalty"):
            cursor.execute("""
                CREATE TABLE Penalty (
                    penalty_id INT AUTO_INCREMENT PRIMARY KEY,
                    penalty_amount DECIMAL(10,2),
                    book_rent_id INT UNIQUE,
                    FOREIGN KEY (book_rent_id) REFERENCES BookRent(book_rent_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Penalty table")
        
        # Wrote table
        if not table_exists("Wrote"):
            cursor.execute("""
                CREATE TABLE Wrote (
                    author_id INT NOT NULL,
                    isbn VARCHAR(20) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    CONSTRAINT wrote_pk PRIMARY KEY (author_id, isbn),
                    CONSTRAINT wrote_fk1 FOREIGN KEY (author_id) REFERENCES Author(author_id),
                    CONSTRAINT wrote_fk2 FOREIGN KEY (isbn) REFERENCES Book(isbn)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created Wrote table")
        
        # Check if Employee table is empty and create default employee
        cursor.execute("SELECT COUNT(*) as count FROM Employee")
        employee_count = cursor.fetchone()[0]
        if employee_count == 0:
            cursor.execute("""
                INSERT INTO Employee (emp_first_name, emp_last_name, start_date)
                VALUES ('System', 'Admin', CURDATE())
            """)
            print("✅ Created default System Admin employee")
        
        # Check if Inventory table is empty and create default inventory
        cursor.execute("SELECT COUNT(*) as count FROM Inventory")
        inventory_count = cursor.fetchone()[0]
        if inventory_count == 0:
            # Get the default employee (should exist now)
            cursor.execute("SELECT employee_id FROM Employee LIMIT 1")
            employee_result = cursor.fetchone()
            if employee_result:
                employee_id = employee_result[0]
                cursor.execute("INSERT INTO Inventory (employee_id) VALUES (%s)", (employee_id,))
                print("✅ Created default inventory")
        
        # Check if categories table is empty and seed default categories
        cursor.execute("SELECT COUNT(*) as count FROM Category")
        category_count = cursor.fetchone()[0]
        if category_count == 0:
            default_categories = [
                ("Fiction", "Fictional stories and novels"),
                ("Non-Fiction", "Non-fictional books and biographies"),
                ("Science", "Science and technology books"),
                ("History", "Historical books and accounts"),
                ("Biography", "Biographical works"),
                ("Mystery", "Mystery and thriller novels"),
                ("Romance", "Romance novels"),
                ("Fantasy", "Fantasy and science fiction"),
                ("Children", "Children's books"),
                ("Education", "Educational and textbook materials"),
            ]
            cursor.executemany(
                "INSERT INTO Category (category_name, description) VALUES (%s, %s)",
                default_categories
            )
            print(f"✅ Seeded {len(default_categories)} default categories")
        
        conn.commit()
        print("\n✅ All tables initialized successfully!")
        
    except Error as e:
        conn.rollback()
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def initialize_database():
    """Main function to initialize database and tables"""
    try:
        print("🚀 Initializing database...")
        create_database_if_not_exists()
        initialize_tables()
        print("\n✅ Database initialization complete!")
    except Error as e:
        print(f"❌ Database initialization failed: {e}")
        raise

