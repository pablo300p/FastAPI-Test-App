#https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?h=oa#hash-and-verify-the-passwords
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .config import settings

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# JWT configurations
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.acces_token_expire_minutes

def create_access_token(data: dict) -> str:
    """
    Creates a JSON Web Token (JWT) access token.
    
    Args:
        data (dict): User data to encode in the token.
    
    Returns:
        str: Encoded JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credential_exception: HTTPException):
    """
    Verifies the validity of a JWT token.

    Args:
        token (str): JWT token to verify.
        credential_exception (HTTPException): Exception to raise if token is invalid.
    
    Returns:
        schemas.TokenData: Token data if the token is valid.
    
    Raises:
        HTTPException: If token is invalid or user ID is missing.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credential_exception
        return schemas.TokenData(id=user_id)
    except JWTError:
        raise credential_exception

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieves the current user from the JWT token.

    Args:
        token (str): JWT token provided by the client.
    
    Returns:
        dict: User information from the database.
    
    Raises:
        HTTPException: If the user is not found or credentials are invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    # Verify token and extract token data
    token_data = verify_access_token(token, credentials_exception)

    # Retrieve user from the database
    db_conn = database.get_connection()
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (token_data.id,))
        user = cursor.fetchone()

        if user is None:
            raise credentials_exception
        return user
    finally:
        if cursor:
            cursor.close()
        database.release_connection(db_conn)


