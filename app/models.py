import psycopg2
from psycopg2.extras import RealDictCursor
from .database import get_connection

# Define SQL statements for table creation
TABLES = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """,
    "posts": """
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            published BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            owner_id INTEGER NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """,
    "votes": """
        CREATE TABLE IF NOT EXISTS votes (
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, post_id),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
        )
    """
}

def create_tables():
    """
    Establishes database connection and creates necessary tables.
    
    Loops through TABLES dictionary to execute each table's creation SQL
    statement if it does not exist. Commits the transaction on success or 
    rolls back on failure. Closes connection resources at the end.
    """
    conn = None
    cursor = None
    try:
        # Connect to the database and create a cursor
        with get_connection() as conn:
            cursor = conn.cursor()

            # Execute each table creation SQL statement
            for table_name, create_statement in TABLES.items():
                cursor.execute(create_statement)

            # Commit the transaction
            conn.commit()
    
    except Exception as e:
        print("An error occurred:", e)
        if conn:
            conn.rollback()
    
    finally:
        # Close cursor and connection if they were created
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
