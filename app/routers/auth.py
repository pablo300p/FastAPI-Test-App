from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, models, schemas, utils, oauth2

# Create an APIRouter instance to define routes related to user authentication
# 'tags' is used to categorize the route in the OpenAPI docs under "Authentication".
router = APIRouter(tags=["Authentication"])

# Define the /login endpoint, which expects a POST request
# This endpoint allows users to log in and obtain an access token
@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), 
          db: Session = Depends(database.get_db)):
    
    # Retrieve the user from the database using the email (OAuth2PasswordRequestForm provides username as email)
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    
    # If the user doesn't exist, raise an HTTP 403 error for "Invalid Credentials"
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    # Verify the provided password using a utility function; raise an error if invalid
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    # Create an access token for the user (JWT) with their user ID encoded in it
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    
    # Return the token as a dictionary with "access_token" and "token_type" for authorization
    return {"access_token": access_token, "token_type": "bearer"}

