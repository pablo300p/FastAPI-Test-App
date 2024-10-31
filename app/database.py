from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from .config import settings

DATABASE_NAME = settings.database_name
DATABASE_USER = settings.database_username
DATABASE_PASSWORD = settings.database_password
DATABASE_HOST = settings.database_hostname
DATABASE_PORT = settings.database_port

# Configure connection pool
pool = pool.SimpleConnectionPool(1, 10, 
                                 user=DATABASE_USER,
                                 password=DATABASE_PASSWORD,
                                 host=DATABASE_HOST,
                                 port=DATABASE_PORT,
                                 database=DATABASE_NAME,
                                 cursor_factory=RealDictCursor)


def get_connection():
    """
    Returns a connection from the connection pool.
    """
    try:
        return pool.getconn()
    except Exception as e:
        print(f"Error getting connection from pool: {e}")
        raise


def release_connection(conn):
    """
    Releases a connection back to the pool.
    """
    pool.putconn(conn)