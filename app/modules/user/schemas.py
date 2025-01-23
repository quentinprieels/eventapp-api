from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import GlobalBase

class UserSchema(GlobalBase):
    """
    Define the User schema
    A user is a person who has an account on the platform.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_picture_key = Column(String, nullable=True, default=None)
    global_role_id = Column(Integer, ForeignKey("global_roles.id"), nullable=False)
    
    global_role = relationship("GlobalRoleSchema", back_populates="users")
    events_users_roles = relationship("EventUserRoleSchema", back_populates="user")
