from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Union
from typing_extensions import Annotated

# Base model to define the common attributes for Post
class PostBase(BaseModel):
    title: str  # Title of the post, required field
    content: str  # Content of the post, required field
    published: bool = True  # Optional field, default value is True
    
    # You can optionally add rating like below:
    # rating: Optional[int] = None 

# Model for creating a post, inherits from PostBase
class PostCreate(PostBase):
    pass  # No additional fields are required for creation, inherits everything from PostBase

# Output model for User data
class UserOut(BaseModel):
    id: int  # Unique user ID
    email: EmailStr  # User's email, validated as a proper email format
    created_at: datetime  # Timestamp for when the user was created

    class Config:
        orm_mode = True  # Enables loading data as ORM objects rather than dicts

# Model to represent a post with owner details
class Post(PostBase):
    id: int  # Unique post ID
    created_at: datetime  # Timestamp for when the post was created
    owner_id: int  # ID of the user who created the post
    owner: UserOut  # User information of the post's owner

    class Config:
        orm_mode = True  # Required to work with ORM objects

# Output model for post details with votes count
class PostOut(BaseModel):
    Post: Post  # Embedded Post model
    votes: int  # Number of votes the post has received

    class Config:
        orm_mode = True  # Required to work with ORM objects

# Input model for creating a new user
class UserCreate(BaseModel):
    email: EmailStr  # User's email
    password: str  # User's password

# Output model for user data
class UserOut(BaseModel):
    id: int  # Unique user ID
    email: EmailStr  # User's email
    created_at: datetime  # Timestamp of user creation

    class Config:
        orm_mode = True  # Required to work with ORM objects

# Model for user login input
class UserLogin(BaseModel):
    email: EmailStr  # Email for login
    password: str  # Password for login

# Model for the access token data
class Token(BaseModel):
    access_token: str  # The token string
    token_type: str  # Type of token, e.g., "Bearer"

# Model for additional token data
class TokenData(BaseModel):
    id: Optional[Union[str, int]] = None  # Optional user ID from token payload

# Model for voting functionality
class Vote(BaseModel):
    post_id: int  # ID of the post being voted on
    dir: Annotated[int, Field(le=1)]  # Vote direction: 1 (upvote), 0 (downvote

