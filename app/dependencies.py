import jwt
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.security import SecurityScopes, OAuth2PasswordBearer

from app.db.base import SessionLocal
from app.core.config import settings
from app.modules.user.models import TokenData, UserMailModel
from app.exceptions import CredentialsException
from app.modules.user.crud import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login", scopes=settings.user_roles_description)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> UserMailModel:
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