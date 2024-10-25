from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings
from pydantic_settings import BaseSettings

#print(settings.database_name)

# CODE IS NOT NEEDED BECAUSE "alembic" manages the connection and creation of tables,
# if Alembic is not used, this code is needed to connect and create database tables.
# Uncomment the line below to connect to the database and create tables.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()  # Initializes the FastAPI application

# List of origins allowed for CORS (Cross-Origin Resource Sharing)
origins = ['*']

# Adds CORS middleware to the FastAPI application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specifies allowed origins
    allow_credentials=True,  # Allows cookies and authentication headers
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in the request
)

# Include routers to organize and handle different routes
app.include_router(post.router)  # Routes for post-related operations
app.include_router(user.router)  # Routes for user-related operations
app.include_router(auth.router)  # Routes for authentication
app.include_router(vote.router)  # Routes for voting-related operations

# Root route that returns a welcome message when the API's root endpoint is accessed
@app.get("/")
def root():
    return {"message": "Welcome to my API"}  # Response with a welcome message





