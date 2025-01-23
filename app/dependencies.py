import jwt
from typing import Annotated
from minio import Minio
from fastapi import Depends
from fastapi.security import SecurityScopes, OAuth2PasswordBearer

from app.db.base import GlobalSessionLocal
from app.core.config import settings
from app.modules.user.models import TokenData, UserMailModel
from app.exceptions import CredentialsException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def get_global_db():
    db = GlobalSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
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
        
    # Add the "global:user" scope in the list of required scopes
    security_scopes.scopes.append("global:user")
    
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