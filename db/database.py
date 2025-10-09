from mysql.connector import pooling
from .conn import DatabaseConnection


db_pool = pooling(pool_name="main_pool",
                  poll_size=5,
                  host="localhost",
                  password="password",
                  user="root",
                  database="IBkit")
#initialize the database connection with your details

database = DatabaseConnection(db_pool)