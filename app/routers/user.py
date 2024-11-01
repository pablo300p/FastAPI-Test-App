from fastapi import APIRouter, status, HTTPException, Depends
from .. import schemas, utils, database
from psycopg2.extras import RealDictCursor

# Initialize router for handling user-related API endpoints
router = APIRouter(
    prefix="/users",   # Prefix all routes with '/users'
    tags=['Users']     # Group documentation under "Users" category
)

# Define a route to create a new user
@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate):
    """
    Create a new user.
    
    Parameters:
    - user: schemas.UserCreate - The user data including email and password.
    
    Returns:
    - Newly created user data (id, email, created_at) if successful.
    """
    try:
        # Get a connection from the pool
        conn = database.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if the user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        existing_user = cursor.fetchone()
        if existing_user:
            # Return a 409 Conflict error if user exists
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user.email} already exists."
            )

        # Hash the password before storing it
        hashed_password = utils.hash(user.password)
        
        # Insert new user data and fetch created_at
        cursor.execute(
            """
            INSERT INTO users (email, password)
            VALUES (%s, %s)
            RETURNING id, email, created_at
            """,
            (user.email, hashed_password)
        )
        new_user = cursor.fetchone()
        
        # Commit the transaction
        conn.commit()
        
        # Return the newly created user, including `created_at`
        return new_user
    
    except HTTPException as http_exc:
        # Propagate HTTP exceptions (e.g., 409 conflict) for proper response
        raise http_exc
    except Exception as e:
        # Handle unexpected errors as 500 errors
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        # Ensure resources are properly released back to the pool
        if conn:
            cursor.close()
            database.release_connection(conn)

# Define a route to get a user by their ID
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int):
    """
    Retrieve a user by their ID.
    
    Parameters:
    - id: int - The unique identifier of the user.
    
    Returns:
    - User data (id, email, created_at) if found.
    """
    conn = None
    try:
        # Get a connection from the pool
        conn = database.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query the database for a user with the specified ID
        cursor.execute("SELECT id, email, created_at FROM users WHERE id = %s", (id,))
        user = cursor.fetchone()
        
        # If user does not exist, raise a 404 error
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {id} does not exist."
            )
        
        # Return the user if found
        return user
    
    except HTTPException as http_exc:
        # Propagate HTTP exceptions (e.g., 404 not found) for proper response
        raise http_exc
    except Exception as e:
        # Handle unexpected errors as 500 errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        # Ensure resources are properly released back to the pool
        if conn:
            cursor.close()
            database.release_connection(conn)



