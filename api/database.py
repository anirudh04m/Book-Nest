import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_SERVER", "localhost"),
    "database": os.getenv("DB_NAME", "BMS"),
    "user": os.getenv("DB_USERNAME", "root"),
    "password": os.getenv("DB_PASSWORD", "sql56789"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

def get_db_connection():
    """
    Get MySQL database connection using mysql-connector-python.
    """
    try:
        conn = mysql.connector.connect(
            host=DATABASE_CONFIG["host"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"],
            database=DATABASE_CONFIG["database"],
            port=DATABASE_CONFIG["port"],
            charset="utf8mb4",
            use_unicode=True
        )

        if conn.is_connected():
            print("✅ Successfully connected to MySQL")
            return conn

    except mysql.connector.Error as e:
        print(f"❌ MySQL Connection Error: {e}")
        raise
