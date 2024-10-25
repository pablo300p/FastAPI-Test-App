from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

# Import models, schemas, and authentication from the app
from .. import models, schemas, oauth2
from ..database import get_db

# Define the API router for posts, with a prefix for all routes
router = APIRouter(
    prefix="/posts",  # All routes will start with /posts
    tags=['Posts']  # Group routes under 'Posts' for documentation purposes
)

# Get all posts, with optional search, limit, and offset query parameters
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),  # Dependency injection for the DB session
    current_user: int = Depends(oauth2.get_current_user),  # Get the current user from OAuth2
    Limit: int = 10,  # Limit the number of posts returned (default is 10)
    Skip: int = 0,  # Number of posts to skip (for pagination)
    Search: Optional[str] = ""  # Optional search string to filter posts by title
):
    # Query posts with vote counts, filtered by the search term, with pagination
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(Search))
        .limit(Limit)
        .offset(Skip)
        .all()
    )
    return posts

# Create a new post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(
    post: schemas.PostCreate,  # Input schema for creating a post
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    # Log the current user's email
    print(current_user.email)

    # Create a new post associated with the current user
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# Get a specific post by ID
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int,  # Post ID to retrieve
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    # Query the post along with vote count
    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )

    # Raise error if the post doesn't exist
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found."
        )
    return post

# Delete a post by ID
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    # Query the post to be deleted
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    # Raise error if the post doesn't exist
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist."
        )

    # Ensure the current user owns the post
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform the requested action"
        )

    # Delete the post and commit changes
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update a post by ID
@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,  # Post ID to update
    updated_post: schemas.PostCreate,  # Input schema for updating a post
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    # Query the post to be updated
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    # Raise error if the post doesn't exist
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist."
        )

    # Ensure the current user owns the post
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform the requested action"
        )

    # Update the post with new data
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
