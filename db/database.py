from mysql.connector import pooling
from .conn import DatabaseConnection
from dotenv import load_dotenv
import os


load_dotenv()

db_pool = pooling( pool_name="main_pool",
    pool_size=5,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"))

database = DatabaseConnection(db_pool)