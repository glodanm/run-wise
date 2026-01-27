import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Activity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), frozen=True)
    user_id: str
    strava_id: int  # Activity ID in Strava
    
    name: str
    distance: float  # in meters 
    moving_time: int  # in seconds
    elapsed_time: int # total time (including pauses)
    total_elevation_gain: float # elevation gain in meters
    type: str  # Run, TrailRun, etc.
    start_date: datetime # start time (UTC)
    
    # Average metrics
    average_speed: float | None = None
    max_speed: float | None = None
    average_heartrate: float | None = None
    max_heartrate: float | None = None
    
    # Raw data (JSON) for future analysis
    raw_data: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True