from pydantic import BaseModel, Field, EmailStr
from app.core.config import settings

password_field = Field(
    pattern=settings.user_password_regex,
    description="Password must meet complexity requirements"
)

# User information models
class UserBaseModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    profile_picture_key: str | None = None
    
class UserRolelModel(UserBaseModel):
    global_role_id: int
    

# User creation and update models
class UserRegisterModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = password_field

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str = password_field

class UserNamesModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    
class UserMailModel(BaseModel):
    email: EmailStr
    
class UserUpdatePasswordModel(BaseModel):
    current_password: str = password_field
    new_password: str = password_field
    
class UserUpdateRoleModel(BaseModel):
    email: EmailStr
    role: str


# Token models
class TokenBase(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    email: str
    roles: list[str]
