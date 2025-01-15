import jwt
from typing import Annotated, OrderedDict
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi import Depends
from fastapi.security import SecurityScopes, OAuth2PasswordBearer

from app.db.base import GlobalSessionLocal
from app.core.config import settings
from app.modules.user.models import TokenData, UserMailModel
from app.exceptions import CredentialsException

# LRU Cache for the database engines
class EngineCache(OrderedDict):
    def __init__(self, capacity: int):
        self.capacity = capacity
        super().__init__()
        
    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value
    
    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self.capacity:
            self.popitem(last=False)   
        
engine_cache = EngineCache(settings.engine_cache_capacity)
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