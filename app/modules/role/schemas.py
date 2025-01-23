from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base import GlobalBase


class RoleSchema:
    """
    Define the Role schema
    A role is a set of permissions that can be assigned to a user.
    """

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    parent_name = Column(String, index=True, nullable=True)
    is_default = Column(Boolean, nullable=False)
    is_admin = Column(Boolean, nullable=False)
    description = Column(String, nullable=True)
    access = Column(String, nullable=False)


class GlobalRoleSchema(RoleSchema, GlobalBase):
    __tablename__ = "global_roles"
    
    users = relationship("UserSchema", back_populates="global_role")


class EventRoleSchema(RoleSchema, GlobalBase):
    __tablename__ = "event_roles"

    events_users_roles = relationship("EventUserRoleSchema", back_populates="event_role")
