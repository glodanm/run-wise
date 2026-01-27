import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, UUID, DateTime, Float, Integer, BigInteger, ForeignKey, JSON
from sqlalchemy.orm import relationship

from src.core.database import Base


class ActivityModel(Base):
    __tablename__ = 'activities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Strava specific fields
    strava_id = Column(BigInteger, unique=True, nullable=False, index=True)
    
    name = Column(String, nullable=False)
    distance = Column(Float, nullable=False) # meters
    moving_time = Column(Integer, nullable=False) # seconds
    elapsed_time = Column(Integer, nullable=False) # seconds
    total_elevation_gain = Column(Float, default=0.0)
    type = Column(String, nullable=False) # Run, TrailRun, etc.
    start_date = Column(DateTime(timezone=True), nullable=False)
    
    # Stats
    average_speed = Column(Float, nullable=True)
    max_speed = Column(Float, nullable=True)
    average_heartrate = Column(Float, nullable=True)
    max_heartrate = Column(Float, nullable=True)
    
    # Raw JSON storage
    raw_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
