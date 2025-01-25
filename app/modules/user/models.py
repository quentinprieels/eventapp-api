from typing import Optional
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
    profile_picture_key: Optional[str] = None
    
class UserDetailModel(UserBaseModel):
    global_roles: list[str]


# User creation and login models
class UserRegisterModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = password_field

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str = password_field


# User update models
class UserUpdateModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    current_password: Optional[str] = Field(
        None,
        pattern=settings.user_password_regex,
        description="Current password required to update user information"
    )
    new_password: Optional[str] = Field(
        None,
        pattern=settings.user_password_regex,
        description="New password must meet complexity requirements"
    )

class UserUpdateRoleModel(BaseModel):
    email: EmailStr
    role: str


# Token models
class TokenBase(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    email: EmailStr
    roles: list[str]
    event_id: Optional[int] = None