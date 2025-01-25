from schwifty import IBAN
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator

from app.core.config import settings

# Event information models
class EventBaseModel(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    logo_key: Optional[str] = None
    
class EventDetailModel(EventBaseModel):
    bank_account: Optional[str] = None
    
    
# Event creation and update models
class EventCreateModel(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    bank_account: Optional[IBAN] = None
    
class EventUpdateModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    bank_account: Optional[str] = None
    logo_key: Optional[str] = None


# Event ID model
class EventIDModel(BaseModel):
    id: int
    
    @field_validator("id")
    def id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("ID must be a positive integer")
        return v