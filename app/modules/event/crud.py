from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import EventCreationException, EventNotFoundException
import app.modules.role.crud as role_crud
import app.modules.user.crud as user_crud
from app.modules.event.models import EventCreateModel, EventBaseModel
from app.modules.event.schemas import EventSchema, EventUserRoleSchema


def _get_and_check_event(db: Session, event_id: int) -> EventSchema:
    db_event = db.query(EventSchema).filter(EventSchema.id == event_id).first()
    if not db_event:
        raise EventNotFoundException()
    return db_event

def _get_and_check_event_user_role(db: Session, user_id: int, event_id: int) -> list[EventUserRoleSchema]:   
    db_event_user_role = db.query(EventUserRoleSchema).filter(
        EventUserRoleSchema.user_id == user_id,
        EventUserRoleSchema.event_id == event_id,
    ).all()
    if not db_event_user_role:
        raise EventNotFoundException()
    return db_event_user_role


def create_event(db: Session, event: EventCreateModel, creator_email: str) -> EventBaseModel:
    try:
        # Start a transaction
        with db.begin():
            # Get the creator user
            creator = user_crud._get_and_check_user_by_email(db, creator_email)
            
            # Create the event
            db_event = EventSchema(
                name=event.name,
                description=event.description if event.description else None,
                start_time=event.start_time,
                end_time=event.end_time,
                bank_account=event.bank_account if event.bank_account else None,
            )
            
            db.add(db_event)
            db.flush()
            
            # Link the creator to the event with the admin event role
            event_admin_role_id = role_crud.get_event_admin_role(db).id
            event_user_role = EventUserRoleSchema(
                user_id=creator.id,
                event_id=db_event.id,
                event_role_id=event_admin_role_id,
            )   
            
            db.add(event_user_role)
            db.flush()
            
            db.refresh(db_event)
            db.refresh(event_user_role)
            return EventBaseModel(**db_event.__dict__)
    except SQLAlchemyError:
        db.rollback()
        raise EventCreationException()    
    return None