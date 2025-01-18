import jwt
from typing import Annotated
from minio import Minio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi import Depends
from fastapi.security import SecurityScopes, OAuth2PasswordBearer

from app.db.base import GlobalSessionLocal
from app.core.config import settings
from app.helpers.cache import LRUCache
from app.modules.user.models import TokenData, UserMailModel
from app.exceptions import CredentialsException

engine_cache = LRUCache(settings.engine_cache_capacity)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login", scopes=settings.user_roles_description)

def get_global_db():
    db = GlobalSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_event_db(event_db_name: str, db: Session = Depends(get_global_db)):
    # Cache the engine for the event database
    if event_db_name not in engine_cache:
        # Check if the event database exists
        # TODO: Implement this
        
        # Get the connection to the event database
        event_db_url = f"{settings.database_url}/{event_db_name}"
        event_engine = create_engine(event_db_url)
        engine_cache[event_db_name] = sessionmaker(autocommit=False, autoflush=False, bind=event_engine)
        
    # Get the session to the event database
    event_db = engine_cache[event_db_name]()
    try:
        yield event_db
    finally:
        event_db.close()
        
def get_minio_db():
    minio_client = Minio(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )
    return minio_client
        
async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]) -> UserMailModel:
    # Format the scopes
    if security_scopes.scopes:
        authenticate_value = f"Bearer scope={security_scopes.scopes}"
    
    # Decode the token and check if it is valid
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise CredentialsException(authenticate_value, "User not found")
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(email=email, roles=token_scopes)
    except jwt.InvalidTokenError:
        raise CredentialsException(authenticate_value, "Invalid token")
    
    # Check if the user has the required scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.roles:
            raise CredentialsException(authenticate_value, "Not enough permissions")
    
    return UserMailModel(email=token_data.email)