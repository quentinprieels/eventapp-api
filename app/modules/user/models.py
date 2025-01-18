from pydantic import BaseModel, Field, EmailStr
from app.core.config import settings

password_field = Field(
    pattern=settings.user_password_regex,
    description="Password must meet complexity requirements"
)

class UserBaseModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    roles: list
    
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
    roles: list[str]

    @classmethod
    def validate_roles(cls, roles: list[str]) -> list[str]:
        invalid_roles = [role for role in roles if role not in settings.user_roles]
        if invalid_roles:
            raise ValueError(f"Invalid roles: {invalid_roles}")
        return roles

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_roles

class TokenBase(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    email: str
    roles: list[str]
