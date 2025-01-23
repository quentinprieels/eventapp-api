from typing import Annotated
from pydantic import ValidationError
from minio import Minio
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Security, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from app.core.config import settings
import app.modules.user.crud as user_crud
import app.modules.role.crud as role_crud
from app.modules.user.models import UserBaseModel, UserRegisterModel, UserLoginModel, UserNamesModel, UserMailModel, UserUpdatePasswordModel, UserUpdateRoleModel, TokenBase
from app.dependencies import get_global_db, get_minio_db, get_current_user
router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# User information routes
@router.get("/me")
def read_users_me(current_user: Annotated[UserMailModel, Depends(get_current_user)], db: Annotated[Session, Depends(get_global_db)]) -> UserBaseModel:
    return user_crud.get_user_by_email(db, current_user.email)
    
@router.get("/profile_picture")
def read_user_profile_picture(current_user: Annotated[UserMailModel, Depends(get_current_user)], db: Annotated[Session, Depends(get_global_db)], minio_db: Annotated[Minio, Depends(get_minio_db)]) -> StreamingResponse:
    return user_crud.get_user_profile_picture(db, minio_db, current_user)

# User creation and update routes
@router.post("/register")
def register(user: UserRegisterModel, db: Annotated[Session, Depends(get_global_db)]) -> UserBaseModel:
    return user_crud.create_user(db, user)

@router.put("/update/names")
def update_user_names(updated_user: UserNamesModel, current_user: Annotated[UserMailModel, Depends(get_current_user)], db: Annotated[Session, Depends(get_global_db)]) -> UserBaseModel:
    return user_crud.update_user_names(db, current_user, updated_user)

@router.put("/update/email")
def update_user_email(updated_user: UserMailModel, current_user: Annotated[UserMailModel, Depends(get_current_user)], db: Annotated[Session, Depends(get_global_db)]) -> UserBaseModel:
    return user_crud.update_user_email(db, current_user, updated_user)

@router.put("/update/password")
def update_user_password(updated_user: UserUpdatePasswordModel, current_user: Annotated[UserMailModel, Depends(get_current_user)], db: Annotated[Session, Depends(get_global_db)]) -> UserBaseModel:
    return user_crud.update_user_password(db, current_user, updated_user)

@router.put("/update/roles")
def update_user_role(updated_user: UserUpdateRoleModel, current_user: Annotated[UserMailModel, Security(get_current_user, scopes=["global:super_admin"])],  db: Annotated[Session, Depends(get_global_db)]) -> UserBaseModel:
    return user_crud.update_user_role(db, updated_user)

@router.put("/update/profile_picture")
async def update_user_profile_picture(profile_picture: UploadFile, current_user: Annotated[UserMailModel, Depends(get_current_user)], db: Annotated[Session, Depends(get_global_db)], minio_db: Annotated[Minio, Depends(get_minio_db)]) -> UserBaseModel:
    return await user_crud.update_user_profile_picture(db, minio_db, current_user, profile_picture)

# User login route
@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_global_db)]) -> TokenBase:
    # Check that the form_data.username is a valid email and that the user exists
    try:
        form_data_user = UserLoginModel(email=form_data.username, password=form_data.password)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
    return user_crud.login_user(db, form_data_user)

# User deletion route
@router.delete("/delete")
def delete_user(current_user: Annotated[UserMailModel, Depends(get_current_user)], db: Annotated[Session, Depends(get_global_db)], minio_db: Annotated[Minio, Depends(get_minio_db)]) -> UserBaseModel:
    return user_crud.delete_user(db, minio_db, current_user)