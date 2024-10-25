from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db

# Create an APIRouter instance for vote-related operations
router = APIRouter(
    prefix="/vote",  # Prefix for all routes in this router
    tags=['Vote']  # Tag to group routes in the FastAPI documentation
)

# Define a POST endpoint to cast or remove a vote
@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Handle voting actions, either adding or deleting a vote on a post.
    
    Parameters:
    - vote: schemas.Vote: The vote data (post ID and direction of vote).
    - db: Session: The database session dependency.
    - current_user: int: The ID of the currently authenticated user (from the OAuth2 token).
    
    Returns:
    - JSON message confirming the action (add or delete vote).
    """
    
    # Check if the post exists
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {vote.post_id} does not exist")

    # Check if the user has already voted on the post
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    # If vote direction is 1 (upvote)
    if vote.dir == 1:
        if found_vote:
            # User already voted, raise a conflict error
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User {current_user.id} already voted the post")
        # Add a new vote to the database
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"Message": "Successfully added vote"}

    # If vote direction is 0 (downvote/remove)
    else:
        if not found_vote:
            # Vote doesn't exist, raise a not found error
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist")
        # Remove the vote from the database
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"Message": "Vote successfully deleted"}

    
