import mysql.connector
import os
from pathlib import Path


def run_migrations():
    """
    Executes all SQL migration files in the 'migrations' directory.

    This function connects to a MySQL database using credentials from environment variables,
    iterates through all `.sql` files in the 'migrations' directory (sorted by filename),
    and executes their contents as SQL statements. After running all migrations, it commits
    the changes and closes the database connection.
    """
    
    conn = mysql.connector.connect(
        host=os.getenv("DB-HOST"),
        port=os.getenv("DB-PORT"),
        password=os.getenv("DB-PASSWORD"),
        database=os.getenv("DB-NAME")
    )

    cursor = conn.cursor()

    migrations_dir = Path(__file__).parent/"migrations"
    for sql_file in sorted(migrations_dir.glob("*.sql")):
        with open(sql_file) as f:
            cursor.exucute(f.read(), multi=True)

if __name__ == "__main__":
    run_migrations()