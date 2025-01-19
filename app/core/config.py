import csv
from pydantic_settings import BaseSettings

def _get_global_roles_and_descriptions_from_csv(file_path) -> dict:
    global_roles = {}
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['categorie'] == 'global':
                global_roles[row['name']] = row['description']
    return global_roles

class Settings(BaseSettings):
    # Application settings
    app_name: str = "EventApp API"
    app_version: str = "0.1.0"
    timezone: str = "Europe/Brussels"
    website_url: str = "https://www.example.com"
    
    # Logging settings
    log_file: str = "app.log"
    log_max_size: int = 100000  # [bytes]
    log_backup_count: int = 3
    
    # Database settings
    database_url: str # See .env file for more details
    database_name: str = "eventapp"
    minio_endpoint: str # See .env file for more details
    minio_access_key: str # See .env file for more details
    minio_secret_key: str # See .env file for more details
    minio_bucket_name: str # See .env file for more details
    minio_secure: bool = False
    engine_cache_capacity: int = 10
    
    # JWT settings
    jwt_secret_key: str # See .env file for more details
    jwt_expiration: int = 3600 * 6 # 6 hours
    jwt_algorithm: str = "HS256" # HMAC-SHA256
    
    # User global roles settings
    roles_csv_path: str = "../resources/roles.csv"
    
    # User password settings
    user_password_regex :str = r"^[A-Za-z\d@$!%*?&]{8,64}$" # Between 8 and 64 characters with at least one letter, one number and one special character
    user_profile_picture_max_size: int = 5 * 1024 * 1024  # 5 MB
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "EVENTAPP_"
      
settings = Settings()