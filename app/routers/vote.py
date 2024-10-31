from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, oauth2
from ..database import get_connection, release_connection

# Create an APIRouter instance for vote-related operations
router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: schemas.Vote,
    current_user: dict = Depends(oauth2.get_current_user)  # Get current user from OAuth2
):
    """
    Handle voting actions, either casting or removing a vote on a post.

    Args:
        vote (schemas.Vote): The vote action to perform.
        current_user (dict): The authenticated user performing the action.

    Returns:
        dict: A message indicating the result of the voting action.
    """
    # Acquire a database connection
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Check if the target post exists
        cursor.execute("SELECT * FROM posts WHERE id = %s", (vote.post_id,))
        post = cursor.fetchone()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {vote.post_id} does not exist"
            )

        # Extract user ID from the current_user dictionary
        user_id = current_user["id"]

        # Check if the user has already voted on the post
        cursor.execute(
            "SELECT * FROM votes WHERE post_id = %s AND user_id = %s",
            (vote.post_id, user_id)
        )
        found_vote = cursor.fetchone()

        # Handle upvote action
        if vote.dir == 1:
            if found_vote:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User {user_id} already voted on the post"
                )

            # Insert new vote into the database
            cursor.execute(
                "INSERT INTO votes (post_id, user_id) VALUES (%s, %s)",
                (vote.post_id, user_id)
            )
            conn.commit()
            return {"Message": "Successfully added vote"}

        # Handle downvote (remove) action
        else:
            if not found_vote:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vote does not exist"
                )

            # Remove the vote from the database
            cursor.execute(
                "DELETE FROM votes WHERE post_id = %s AND user_id = %s",
                (vote.post_id, user_id)
            )
            conn.commit()
            return {"Message": "Vote successfully deleted"}
    finally:
        # Ensure the connection is released back to the pool
        release_connection(conn)


