from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application settings
    app_name: str = "EventApp API"
    app_version: str = "0.1.0"
    timezone: str = "Europe/Brussels"
    website_url: str = "https://www.example.com"
    
    # Database settings
    database_url: str                           # See .env file for more details
    
    # JWT settings
    jwt_secret_key: str                         # See .env file for more details
    jwt_expiration: int = 3600                  # 1 hour
    jwt_algorithm: str = "HS256"                # HMAC-SHA256
    
    # User settings
    user_roles_description: dict = {
        "admin": "Administrator",
        "user": "User"
    }
    user_roles : list = list(user_roles_description.keys())
    user_default_role: str = "user"
    user_password_regex :str = r"^[A-Za-z\d@$!%*?&]{8,64}$"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "EVENTAPP_"
    
        
        
settings = Settings()