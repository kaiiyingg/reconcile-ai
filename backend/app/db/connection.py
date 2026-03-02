import os
import psycopg2
from dotenv import load_dotenv # type: ignore

load_dotenv()  # Load environment variables from .env file

# Supabase/PostgreSQL connection details from .env
# Using Supabase naming convention (lowercase)
USER = os.getenv('user')
PASSWORD = os.getenv('password') 
HOST = os.getenv('host')
PORT = os.getenv('port') 
DBNAME = os.getenv('dbname') 

"""
This module handles database connections and schema/index creation for the ReconcileAI application.
It loads database credentials from environment variables and uses psycopg2 to interact with PostgreSQL/Supabase.
Run "python app/db/connection.py" to create tables, indexes, and metadata tables based on SQL scripts in the same directory.

All .sql files in this directory will be executed, including:
"""

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        print("Connection successful!")
        return conn
    except Exception as e:
        print(f"Failed to connect: {e}")
        raise

def close_db_connection(conn):
    """Closes the database connection."""
    if conn:
        conn.close()

def create_tables():
    """
    Executes all .sql files in the current directory to create tables, indexes, and other schema objects.
    Reads each .sql file, executes its content (including multiple statements per file), and commits the changes.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql_dir = os.path.dirname(os.path.abspath(__file__))
        sql_files = [f for f in os.listdir(sql_dir) if f.endswith('.sql')]
        sql_files.sort()
        for sql_file in sql_files:
            file_path = os.path.join(sql_dir, sql_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                sql = f.read()
                if 'CREATE INDEX CONCURRENTLY' in sql.upper():
                    print(f"Executing {sql_file} in autocommit mode (for CONCURRENTLY indexes)...")
                    # Split into individual statements (naive split on semicolon, but only for CREATE INDEX CONCURRENTLY)
                    statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
                    for stmt in statements:
                        if 'CREATE INDEX CONCURRENTLY' in stmt.upper():
                            import psycopg2
                            conn_ac = psycopg2.connect(
                                user=USER,
                                password=PASSWORD,
                                host=HOST,
                                port=PORT,
                                dbname=DBNAME
                            )
                            conn_ac.autocommit = True
                            cursor_ac = conn_ac.cursor()
                            cursor_ac.execute(stmt)
                            print(f"Executed: {stmt[:60]}...")
                            cursor_ac.close()
                            conn_ac.close()
                else:
                    cursor.execute(sql)
                    print(f"Executed {sql_file}")
        conn.commit()
        print("All SQL scripts executed and tables created successfully.")
    except Exception as e:
        print(f"An error occurred while creating tables: {e}")
    finally:
        close_db_connection(conn)

if __name__ == '__main__':
    load_dotenv()  # Load env variables here so they are available when run directly.
    print("Attempting to create database tables from SQL files...")
    create_tables()
    print("Database table creation process completed.")