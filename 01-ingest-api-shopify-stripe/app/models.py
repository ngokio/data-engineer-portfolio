from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from .database import Base

class DataEvent(Base):
    __tablename__ = "data_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(100), nullable=False, index=True)  # ex: shopify, csv_import
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, nullable=True)
    amount = Column(Float, nullable=True)
    payload = Column(JSON, nullable=False)  # On garde tout le brut ici
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), index=True)

    __table_args__ = (
        Index('ix_source_event_type', 'source', 'event_type'),
    )
