from pydantic_settings import BaseSettings

# This class is used to manage and validate environment variables for application configuration.
# It inherits from BaseSettings, which automatically loads values from environment variables.
class Settings(BaseSettings):
    
    # Define application settings, which will be filled with values from the environment.
    # These fields correspond to essential database and security configuration values.
    database_hostname: str         # Database host name
    database_port: str             # Database port number
    database_password: str         # Database password
    database_name: str             # Name of the database
    database_username: str         # Database user
    secret_key: str                # Secret key for JWT or other cryptographic operations
    algorithm: str                 # Algorithm used for cryptographic operations
    acces_token_expire_minutes: int # Access token expiration time in minutes
    
    # Config class allows customization of how the environment variables are loaded.
    # 'env_file' specifies that the environment variables should be read from the .env file this is for local.
    class Config:
        env_file = ".env"

# Instantiate the settings, automatically loading values from environment variables or the .env file.
settings = Settings()
