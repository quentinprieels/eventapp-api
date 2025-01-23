from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import GlobalBase


class EventSchema(GlobalBase):
    """
    Define the Event schema
    An event is a gathering of people for a specific purpose.
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    bank_account = Column(String, nullable=True)
    logo_key = Column(String, nullable=True)
    
    events_users_roles = relationship("EventUserRoleSchema", back_populates="event")
    
    
class EventUserRoleSchema(GlobalBase):
    """
    Define the EventUserRole schema
    An EventUserRole is the role that a user has in an event.
    """
    
    __tablename__ = "events_users_roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    event_role_id = Column(Integer, ForeignKey("event_roles.id"), nullable=False)
    
    user = relationship("UserSchema", back_populates="events_users_roles")
    event = relationship("EventSchema", back_populates="events_users_roles")
    event_role = relationship("EventRoleSchema", back_populates="events_users_roles")
