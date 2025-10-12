import mysql.connector
import os
from pathlib import Path


def run_migrations():
    """
    Executes all SQL migration files in the 'migrations' directory.
    """
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = conn.cursor()

    migrations_dir = Path(__file__).parent / "migrations"
    for sql_file in sorted(migrations_dir.glob("*.sql")):
        with open(sql_file) as f:
            sql_statements = f.read()
            for result in cursor.execute(sql_statements, multi=True):
                if result.with_rows:
                    result.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_migrations()