from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List, Optional
from .. import schemas, oauth2, database

# Define the API router for posts, with a prefix for all routes
router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# Get all posts with optional search, limit, and offset query parameters
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):
    query = """
        SELECT p.id, p.title, p.content, p.published, p.created_at, p.owner_id,
               u.id AS owner_id, u.email AS owner_email, u.created_at AS owner_created_at,
               COALESCE(count(v.post_id), 0) AS votes
        FROM posts p
        LEFT JOIN users u ON u.id = p.owner_id
        LEFT JOIN votes v ON v.post_id = p.id
        WHERE p.title ILIKE %s
        GROUP BY p.id, u.id
        LIMIT %s OFFSET %s
    """
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(query, (f"%{search}%", limit, skip))
    raw_posts = cursor.fetchall()
    cursor.close()

    # Transform raw query results to the expected format
    posts = [
        {
            "Post": {
                "id": post["id"],
                "title": post["title"],
                "content": post["content"],
                "published": post["published"],
                "created_at": post["created_at"],
                "owner_id": post["owner_id"],
                "owner": {
                    "id": post["owner_id"],
                    "email": post["owner_email"],
                    "created_at": post["owner_created_at"]
                }
            },
            "votes": post["votes"]
        }
        for post in raw_posts
    ]
    return posts


# Create a new post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    current_user: dict = Depends(oauth2.get_current_user)
):
    query = """
        INSERT INTO posts (title, content, owner_id)
        VALUES (%s, %s, %s) RETURNING *
    """
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(query, (post.title, post.content, current_user['id']))
    new_post = cursor.fetchone()

    # Fetch owner details
    user_query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(user_query, (new_post['owner_id'],))
    user = cursor.fetchone()
    new_post['owner'] = user

    conn.commit()
    cursor.close()
    return new_post


# Get a specific post by ID
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int,
    current_user: int = Depends(oauth2.get_current_user)
):
    query = """
        SELECT p.id, p.title, p.content, p.published, p.created_at, p.owner_id,
               u.id AS owner_id, u.email AS owner_email, u.created_at AS owner_created_at,
               COALESCE(count(v.post_id), 0) AS votes
        FROM posts p
        LEFT JOIN users u ON u.id = p.owner_id
        LEFT JOIN votes v ON v.post_id = p.id
        WHERE p.id = %s
        GROUP BY p.id, u.id
    """
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(query, (id,))
    post = cursor.fetchone()
    cursor.close()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found.")

    post_data = {
        "Post": {
            "id": post["id"],
            "title": post["title"],
            "content": post["content"],
            "published": post["published"],
            "created_at": post["created_at"],
            "owner_id": post["owner_id"],
            "owner": {
                "id": post["owner_id"],
                "email": post["owner_email"],
                "created_at": post["owner_created_at"]
            }
        },
        "votes": post["votes"]
    }
    return post_data


# Delete a post by ID
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    current_user: dict = Depends(oauth2.get_current_user)
):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    post = cursor.fetchone()

    if not post:
        cursor.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} does not exist.")
    
    if post["owner_id"] != current_user["id"]:
        cursor.close()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform the requested action")
    
    cursor.execute("DELETE FROM posts WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Update a post by ID
@router.put("/{id}", response_model=schemas.PostOut)
def update_post(
    id: int,
    updated_post: schemas.PostCreate,
    current_user: dict = Depends(oauth2.get_current_user)
):
    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    post = cursor.fetchone()
    if not post:
        cursor.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} does not exist.")
    
    if post["owner_id"] != current_user["id"]:
        cursor.close()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform the requested action")
    
    update_query = """
        UPDATE posts SET title = %s, content = %s WHERE id = %s RETURNING id, title, content, published, created_at, owner_id
    """
    cursor.execute(update_query, (updated_post.title, updated_post.content, id))
    updated_post_data = cursor.fetchone()

    cursor.execute("SELECT id, email, created_at FROM users WHERE id = %s", (updated_post_data["owner_id"],))
    owner_data = cursor.fetchone()

    conn.commit()
    cursor.close()

    response_data = {
        "Post": {
            "id": updated_post_data["id"],
            "title": updated_post_data["title"],
            "content": updated_post_data["content"],
            "published": updated_post_data["published"],
            "created_at": updated_post_data["created_at"],
            "owner_id": updated_post_data["owner_id"],
            "owner": {
                "id": owner_data["id"],
                "email": owner_data["email"],
                "created_at": owner_data["created_at"]
            }
        },
        "votes": 0  # Default votes to 0 or fetch current vote count if needed
    }
    return response_data
