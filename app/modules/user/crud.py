import bcrypt
import jwt
import re
import io
from minio.error import S3Error
from datetime import datetime, timedelta, timezone
from minio import Minio
from sqlalchemy.orm import Session
from fastapi import UploadFile
from fastapi.responses import StreamingResponse

from app.exceptions import UserAlreadyExists, UserNotFound, InvalidPassword, RoleNotAssignable, InvalidImage, ImageNotFound
from app.core.config import settings
from app.modules.user.schemas import UserSchema
from app.modules.user.models import UserBaseModel, UserRegisterModel, UserLoginModel, UserNamesModel, UserMailModel, UserUpdatePasswordModel, UserUpdateRoleModel, TokenBase
import app.modules.role.crud as role_crud

# Password hashing and verification
def _get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# User global roles management
def _is_last_global_admin(db: Session, user: UserSchema) -> bool:
    global_admin_role_id = role_crud.get_default_admin_role(db).id
    is_user_global_admin = user.global_role_id == global_admin_role_id
    number_of_global_admins = db.query(UserSchema).filter(UserSchema.global_role_id == global_admin_role_id).count()
    return is_user_global_admin and number_of_global_admins == 1

# JWT token creation
def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# Databases getters
def _get_user_by_email(db: Session, email: str) -> UserSchema:
    return db.query(UserSchema).filter(UserSchema.email == email).first()

def _get_and_check_user_by_email(db: Session, email: str) -> UserSchema:
    db_user = _get_user_by_email(db, email)
    if not db_user:
        raise UserNotFound()
    return db_user


# User information
def get_user_by_email(db: Session, email: str) -> UserBaseModel:
    db_user = _get_and_check_user_by_email(db, email)
    return UserBaseModel(**db_user.__dict__)

def get_user_profile_picture(db: Session, minio_db: Minio, current_user: UserMailModel) -> UploadFile:
    db_user = _get_and_check_user_by_email(db, current_user.email)
    if not db_user.profile_picture_key:
        raise ImageNotFound()
    profile_picture = minio_db.get_object(settings.minio_bucket_name, db_user.profile_picture_key)
    return StreamingResponse(profile_picture, media_type=profile_picture.headers.get("Content-Type"))

def update_user_names(db: Session, current_user: UserMailModel, updated_user: UserNamesModel) -> UserBaseModel:
    db_user = _get_and_check_user_by_email(db, current_user.email)
    if updated_user.first_name: db_user.first_name = updated_user.first_name
    if updated_user.last_name: db_user.last_name = updated_user.last_name
    db.commit()
    db.refresh(db_user)
    return UserBaseModel(**db_user.__dict__)

async def update_user_profile_picture(db: Session, minio_db: Minio, current_user: UserMailModel, profile_picture: UploadFile) -> UserBaseModel:
    # Check if the file is a valid image
    if not profile_picture.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise InvalidImage("Only PNG and JPG files are allowed")
    if not profile_picture.content_type.startswith("image"):
        raise InvalidImage("Invalid image file")
    if profile_picture.size > settings.user_profile_picture_max_size:
        raise InvalidImage("Image file too large")
    
    # Update the user's profile picture
    db_user = _get_and_check_user_by_email(db, current_user.email)
    
    # Process the image
    try:
        profile_picture_key = f"{current_user.email}/{profile_picture.filename.replace('/', '')}"
        profile_picture_key = re.sub(r'[^a-zA-Z0-9/_.]', '', profile_picture_key).replace(" ", "_").lower()
        profile_picture_image = await profile_picture.read()    
        
        # Delete the previous profile picture
        if db_user.profile_picture_key:
            minio_db.remove_object(settings.minio_bucket_name, db_user.profile_picture_key)
            
        # Upload the new profile picture
        minio_db.put_object(settings.minio_bucket_name, profile_picture_key,io.BytesIO(profile_picture_image), len(profile_picture_image), profile_picture.content_type)
        db_user.profile_picture_key = profile_picture_key
        db.commit()
        db.refresh(db_user)
    except S3Error:
        raise InvalidImage("Error while uploading the image")
    return UserBaseModel(**db_user.__dict__)

def update_user_email(db: Session, current_user: UserMailModel, updated_user: UserMailModel) -> UserBaseModel:
    db_user = _get_and_check_user_by_email(db, current_user.email)
    db_user_with_same_new_email = _get_user_by_email(db, updated_user.email)
    if db_user_with_same_new_email:
        raise UserAlreadyExists()
    db_user.email = updated_user.email
    db.commit()
    db.refresh(db_user)
    return UserBaseModel(**db_user.__dict__)

def update_user_password(db: Session, current_user: UserMailModel, updated_user: UserUpdatePasswordModel) -> UserBaseModel:
    db_user = _get_and_check_user_by_email(db, current_user.email)
    if not _verify_password(updated_user.current_password, db_user.hashed_password):
        raise InvalidPassword()
    db_user.hashed_password = _get_hashed_password(updated_user.new_password)
    db.commit()
    db.refresh(db_user)
    return UserBaseModel(**db_user.__dict__)

def update_user_role(db: Session, update_role_user: UserUpdateRoleModel) -> UserBaseModel:   
    db_user = _get_and_check_user_by_email(db, update_role_user.email)
    
    # Check that the new role is a valid global role
    new_role = role_crud.get_global_role_by_name(db, update_role_user.role)
    
    # Do not allow a solitary admin to remove his role
    if _is_last_global_admin(db, db_user) and not new_role.is_admin:
        raise RoleNotAssignable("At least one user must have the 'admin' role")
    
    db_user.global_role_id = new_role.id
    db.commit()
    db.refresh(db_user)
    return UserBaseModel(**db_user.__dict__)


# User creation
def create_user(db: Session, user: UserRegisterModel) -> UserBaseModel:
    if _get_user_by_email(db, user.email):
        raise UserAlreadyExists()
    db_user = UserSchema(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=_get_hashed_password(user.password),
        global_role_id=role_crud.get_default_global_role(db).id
    )
    
    # If the first user is created, assign the default admin role
    if not db.query(UserSchema).count():
        db_user.global_role_id = role_crud.get_default_admin_role(db).id
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserBaseModel(**db_user.__dict__)      


# User authentication
def login_user(db: Session, user: UserLoginModel) -> TokenBase:
    db_user = _get_and_check_user_by_email(db, user.email)
    if not _verify_password(user.password, db_user.hashed_password):
        raise InvalidPassword()
    
    access_token_expires = timedelta(minutes=settings.jwt_expiration)
    access_token_data = {"sub": user.email, "scopes": role_crud.get_user_global_roles_jwt_format(db, db_user.global_role_id)}
    access_token = create_access_token(data=access_token_data,expires_delta=access_token_expires)
    return TokenBase(access_token=access_token, token_type="bearer")


# User deletion
def delete_user(db: Session, minio_db: Minio, current_user: UserMailModel) -> UserBaseModel:
    db_user = _get_and_check_user_by_email(db, current_user.email)
    
    # Chek that the user is not the last admin
    if _is_last_global_admin(db, db_user):
        raise RoleNotAssignable("At least one user must have the 'admin' role")
    
    # Delete the user's profile picture
    if db_user.profile_picture_key:
        minio_db.remove_object(settings.minio_bucket_name, db_user.profile_picture_key)
        
    # Delete the user
    db.delete(db_user)
    db.commit()
    return UserBaseModel(**db_user.__dict__)
