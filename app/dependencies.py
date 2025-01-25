import jwt
from typing import Annotated
from minio import Minio
from sqlalchemy.orm import Session
from fastapi import Depends, status
from fastapi.security import SecurityScopes, OAuth2PasswordBearer

from app.db.base import GlobalSessionLocal
from app.core.config import settings
from app.modules.user.models import TokenData, TokenData
from app.exceptions import CredentialsException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token/new")

# Dependency functions
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
        
async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
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
            raise CredentialsException(authenticate_value, detail="User not found")
        token_scopes = payload.get("scopes", [])
        token_event_id = payload.get("event_id", None)
        token_data = TokenData(email=email, roles=token_scopes, event_id=token_event_id)
    except jwt.InvalidTokenError:
        raise CredentialsException(authenticate_value, detail="Invalid token")
    
    # Check if the user has the required scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.roles:
            raise CredentialsException(authenticate_value, detail="Not enough permissions", status_code=status.HTTP_403_FORBIDDEN)
    
    return token_data

# Intermediary dependencies
GlobalDB = Annotated[Session, Depends(get_global_db)]
MinioDB = Annotated[Minio, Depends(get_minio_db)]
CurrentUser = Annotated[TokenData, Depends(get_current_user)]
