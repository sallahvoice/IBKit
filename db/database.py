import os

from dotenv import load_dotenv
from mysql.connector import pooling

from .conn import DatabaseConnection

load_dotenv()

db_pool = pooling.MySQLConnectionPool(
    pool_name="main_pool",
    pool_size=5,
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 3306),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
)

database = DatabaseConnection(db_pool)
