from typing import Annotated
from datetime import timedelta
from pydantic import ValidationError
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
import app.modules.user.crud as user_crud
from app.modules.user.models import UserRegisterModel, UserLoginModel, UserUpdateModel, UserUpdateRoleModel, UserBaseModel, UserMailModel, TokenBase
from app.dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/me")
async def read_users_me(current_user: Annotated[UserMailModel, Depends(get_current_user)]) -> UserBaseModel:
    return user_crud.get_user_by_email(current_user.email)
    
@router.post("/register")
async def register(user: UserRegisterModel, db: Annotated[Session, Depends(get_db)]) -> UserBaseModel:
    return user_crud.create_user(db, user)

@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]) -> TokenBase:
    # Check that the form_data.username is a valid email and that the user exists
    try:
        form_data_user = UserLoginModel(email=form_data.username, password=form_data.password)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
    user = user_crud.login_user(db, form_data_user)
    
    # Create the access token
    access_token_expires = timedelta(minutes=settings.jwt_expiration)
    access_token_data = {"sub": user.email, "scopes": user.roles}
    access_token = user_crud.create_access_token(data=access_token_data,expires_delta=access_token_expires)
    return TokenBase(access_token=access_token, token_type="bearer")

@router.put("/update")
async def update_user(updated_user: UserUpdateModel, current_user: Annotated[UserMailModel, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> UserBaseModel:
    return user_crud.update_user(db, current_user, updated_user)

@router.put("/update/roles")
async def update_user_roles(updated_user: UserUpdateRoleModel, current_user: Annotated[UserMailModel, Security(get_current_user, scopes=["admin"])],  db: Annotated[Session, Depends(get_db)]) -> UserBaseModel:
    return user_crud.update_user_roles(db, updated_user)