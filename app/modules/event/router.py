from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Security, HTTPException, status

import app.modules.event.crud as event_crud
from app.modules.user.models import TokenData
from app.modules.event.models import EventCreateModel, EventUpdateModel
from app.dependencies import GlobalDB, CurrentUser, get_current_user

router = APIRouter(
    prefix="/event",
    tags=["event"],
)


# Event creation route
@router.post("/new")
def create_event(event: EventCreateModel, current_user: CurrentUser, db: GlobalDB):
    return event_crud.create_event(db, event, current_user.email)
