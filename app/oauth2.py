#https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?h=oa#hash-and-verify-the-passwords
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

# OAuth2PasswordBearer is a class to retrieve the token from the 'Authorization' header
# It requires a token URL, which is typically the login endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# Configuration for JWT (JSON Web Token) encoding and decoding
# These values are imported from a configuration file for security
SECRET_KEY = settings.secret_key  # Secret key used to encode and decode JWT
ALGORITHM = settings.algorithm  # Algorithm used to sign the JWT, such as HS256
ACCESS_TOKEN_EXPIRE_MINUTES = settings.acces_token_expire_minutes  # Expiration time for tokens



# Function to create an access token using JWT
# Input: data (dictionary containing user information to encode into the token)
# Output: JWT string that contains the encoded information
def create_access_token(data: dict):
    to_encode = data.copy()  # Copy the input data to avoid modifying the original
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Set expiration time
    to_encode.update({"exp": expire})  # Add expiration time to the token's payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode and sign the token
    return encoded_jwt  # Return the JWT token



# Function to verify the validity of an access token
# Input: token (JWT), credential_exception (custom exception to raise on failure)
# Output: token_data (extracted and verified information from the token)
def verify_access_token(token: str, credential_exception):
    try:
        # Decode the JWT token using the secret key and the defined algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")  # Extract 'user_id' from the payload
        
        if user_id is None:
            raise credential_exception  # Raise exception if 'user_id' is not present
        token_data = schemas.TokenData(id=user_id)  # Create a token data object with the user_id
    except JWTError:
        raise credential_exception  # Raise exception if token is invalid or tampered with
    
    return token_data  # Return the verified token data




# Function to get the current user based on the token
# Input: token (extracted by FastAPI from request header), db (database session)
# Output: the user object from the database
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    # Custom exception for invalid credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    token = verify_access_token(token, credentials_exception)  # Verify the token
    user = db.query(models.User).filter(models.User.id == token.id).first()  # Query the user from the database
    
    return user  # Return the user object
