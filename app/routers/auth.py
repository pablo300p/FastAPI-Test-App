from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from psycopg2 import sql
from psycopg2.extensions import connection as Connection
from .. import database, schemas, utils, oauth2

# Initialize APIRouter for authentication-related routes
router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to authenticate users and return an access token.
    
    Parameters:
    - user_credentials (OAuth2PasswordRequestForm): Contains user login credentials (email and password).
    
    Returns:
    - JSON object with access token and token type.
    """
    # Obtain a database connection from the pool
    conn: Connection = database.get_connection()
    try:
        cursor = conn.cursor()
        
        # Retrieve user data from the database using the email
        cursor.execute(
            sql.SQL("SELECT id, password FROM users WHERE email = %s"),
            [user_credentials.username]
        )
        user = cursor.fetchone()
        
        # Check if user exists
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid Credentials"
            )
        
        user_id, hashed_password = user['id'], user['password']
        
        # Verify provided password matches the stored hashed password
        if not utils.verify(user_credentials.password, hashed_password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid Credentials"
            )
        
        # Generate a JWT access token containing the user ID
        access_token = oauth2.create_access_token(data={"user_id": user_id})
        
        # Return token as JSON response
        return {"access_token": access_token, "token_type": "bearer"}
    
    finally:
        # Ensure cursor is closed and connection is released back to the pool
        cursor.close()
        database.release_connection(conn)
