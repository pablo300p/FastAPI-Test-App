from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

# Create a new router for handling user-related API endpoints.
# This will automatically group endpoints under the '/users' path
# and group them under the "Users" section in the API documentation.
router = APIRouter(
    prefix="/users",          # Prefix all routes with '/users'
    tags=['Users']            # Group documentation under "Users" category
)

# Define a route to create a new user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user in the system.

    Parameters:
    - user: UserCreate schema containing user data like email and password.
    - db: The database session used to query and save user information.

    Returns:
    - The created user as a response model.
    """
    
    # Check if the user with the provided email already exists in the database
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    if existing_user:
        # If the user exists, return a 409 Conflict error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {user.email} already exists."
        )
    
    # Hash the user's password before storing it in the database
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    # Create a new user instance from the provided user data
    new_user = models.User(**user.dict())
    
    # Add the new user to the database and commit the transaction
    db.add(new_user)
    db.commit()
    
    # Refresh the user instance to reflect the committed changes (such as generated ID)
    db.refresh(new_user)
    
    # Return the newly created user
    return new_user





# Define a route to get a user by their ID
@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    """
    Fetches a user by their ID.

    Parameters:
    - id: The ID of the user to retrieve.
    - db: The database session used to query the user.

    Returns:
    - The user with the specified ID if found, otherwise a 404 error.
    """
    
    # Query the database for a user with the specified ID
    user = db.query(models.User).filter(models.User.id == id).first()
    
    # If the user does not exist, return a 404 Not Found error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist"
        )
    
    # Return the user if found
    return user
