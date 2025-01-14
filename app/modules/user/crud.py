import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.exceptions import UserAlreadyExists, UserNotFound, InvalidPassword, RoleNotAssignable
from app.core.config import settings
from app.modules.user.schemas import UserSchema
from app.modules.user.models import UserRegisterModel, UserLoginModel, UserBaseModel, UserUpdateModel, UserMailModel, UserUpdateRoleModel

def _get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def get_user_by_email(db: Session, email: str) -> UserSchema:
    return db.query(UserSchema).filter(UserSchema.email == email).first()

def login_user(db: Session, user: UserLoginModel) -> UserBaseModel:
    db_user = get_user_by_email(db, user.email)
    if not user:
        raise UserNotFound()
    if not _verify_password(user.password, db_user.hashed_password):
        raise InvalidPassword()
    return UserBaseModel(**db_user.__dict__)

def create_user(db: Session, user: UserRegisterModel) -> UserBaseModel:
    if get_user_by_email(db, user.email):
        raise UserAlreadyExists()
    db_user = UserSchema(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=_get_hashed_password(user.password),
        roles=[settings.user_default_role]
    )
    if not db.query(UserSchema).count():
        db_user.roles = settings.user_roles
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserBaseModel(**db_user.__dict__)      

def update_user(db: Session, current_user: UserMailModel, updated_user: UserUpdateModel) -> UserBaseModel:
    db_user = get_user_by_email(db, current_user.email)
    if not db_user:
        raise UserNotFound()
    if updated_user.first_name: db_user.first_name = updated_user.first_name
    if updated_user.last_name: db_user.last_name = updated_user.last_name
    if updated_user.email: db_user.email = updated_user.email
    if updated_user.password: db_user.hashed_password = _get_hashed_password(updated_user.password)
    db.commit()
    db.refresh(db_user)
    return UserBaseModel(**db_user.__dict__)

def update_user_roles(db: Session, update_roles_user: UserUpdateRoleModel) -> UserBaseModel:   
    db_user = get_user_by_email(db, update_roles_user.email)
    if not db_user:
        raise UserNotFound()
    
    # Do not allow a solitary admin to remove his role
    if "admin" not in update_roles_user.roles:
        number_admin_users = db.query(UserSchema).filter(UserSchema.roles.any("admin")).count()
        if number_admin_users == 1 and "admin" in db_user.roles:
            raise RoleNotAssignable("At least one user must have the 'admin' role")
        
    db_user.roles = update_roles_user.roles
    db.commit()
    db.refresh(db_user)
    return UserBaseModel(**db_user.__dict__)