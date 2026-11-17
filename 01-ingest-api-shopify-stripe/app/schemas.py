from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

# Ce que le client t'envoie
class EventCreate(BaseModel):
    source: str = Field(..., examples=["shopify"])
    event_type: str = Field(..., examples=["purchase"])
    user_id: Optional[int] = None
    amount: Optional[float] = Field(None, ge=0)
    payload: dict = Field(default_factory=dict)

class BulkCreate(BaseModel):
    events: List[EventCreate] = Field(..., max_length=10000)

# Ce que tu renvoies (mise à disposition)
class EventRead(BaseModel):
    id: UUID
    source: str
    event_type: str
    user_id: Optional[int]
    amount: Optional[float]
    payload: dict
    created_at: datetime

    class Config:
        from_attributes = True
