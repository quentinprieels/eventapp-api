from typing import Annotated
from pydantic import ValidationError
from fastapi import APIRouter, Depends, Security, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

import app.modules.user.crud as user_crud
from app.modules.user.models import UserBaseModel, UserDetailModel, UserRegisterModel, UserLoginModel, UserUpdateModel, TokenData, UserUpdateRoleModel, TokenBase
from app.dependencies import GlobalDB, MinioDB, CurrentUser, get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

# User information routes
@router.get("/me")
def get_user_info(current_user: CurrentUser, db: GlobalDB) -> UserDetailModel:
    return user_crud.get_user_informations(db, current_user.email)
    
@router.get("/me/profile_picture")
def read_user_profile_picture(current_user: CurrentUser, db: GlobalDB, minio_db: MinioDB) -> StreamingResponse:
    return user_crud.get_user_profile_picture(db, minio_db, current_user)


# User login route
@router.post("/token/new")
def get_user_global_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: GlobalDB) -> TokenBase:
    # Check that the form_data.username is a valid email and that the user exists
    try:
        form_data_user = UserLoginModel(email=form_data.username, password=form_data.password)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
    return user_crud.get_token_with_global_roles(db, form_data_user)

@router.post("/token/refresh")
def get_user_event_token(event_id: int, current_user: CurrentUser, db: GlobalDB) -> TokenBase:
    return user_crud.get_token_with_global_and_event_roles(db, current_user, event_id)


# User registration route
@router.post("/new")
def create_user(user: UserRegisterModel, db: GlobalDB) -> UserBaseModel:
    return user_crud.create_user(db, user)


# User update routes
@router.put("/me/infos")
def update_user_informations(updated_user: UserUpdateModel, current_user: CurrentUser, db: GlobalDB) -> UserBaseModel:
    return user_crud.update_user(db, current_user, updated_user)

@router.put("/me/profile_picture")
async def update_user_profile_picture(profile_picture: UploadFile, current_user: CurrentUser, db: GlobalDB, minio_db: MinioDB) -> UserBaseModel:
    return await user_crud.update_user_profile_picture(db, minio_db, current_user, profile_picture)

@router.put("/role")
def update_user_global_role(updated_user: UserUpdateRoleModel, current_user: Annotated[TokenData, Security(get_current_user, scopes=["global:super_admin"])],  db: GlobalDB) -> UserBaseModel:
    return user_crud.update_user_role(db, updated_user)


# User deletion route
@router.delete("/me")
def delete_user(current_user: CurrentUser, db: GlobalDB, minio_db: MinioDB) -> UserBaseModel:
    return user_crud.delete_user(db, minio_db, current_user)
