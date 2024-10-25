from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings

# Define the connection string using environment variables from the config file
# The format is: 'postgresql://username:password@hostname:port/dbname'
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

# Create the SQLAlchemy engine which manages the database connection pool
# This is used to interact with the PostgreSQL database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Configure a session factory using sessionmaker
# This session factory is used to create new database sessions which manage transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for ORM models, which is used to define database tables
Base = declarative_base()

# Dependency for database sessions
# This function yields a new database session, automatically closing it after use
def get_db():
    """
    Creates a new SQLAlchemy database session and ensures that it gets closed 
    properly after the request is completed.
    
    Yields:
    - db: An active database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# while True:
#     try:
#         conn = psycopg2.connect(host = 'localhost', database = 'fastapi', user = 'postgres', password = '$Password1234p', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Databse connection was sucesfull!")
#         break
#     except Exception as error:
#         print("Database connection failed!")
#         print("Error: ", error)
#         time.sleep(5)
    
