from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import post, user, auth, vote
from .models import create_tables  # Import the function to create tables

app = FastAPI()

# Configure CORS middleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()  # Ensures tables are created if they don't exist

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to my API"}




