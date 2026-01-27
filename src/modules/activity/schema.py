from typing import Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class StravaWebhookEvent(BaseModel):
    object_type: str  # "activity" or "athlete"
    object_id: int    # Activity ID in Strava
    aspect_type: str  # "create", "update", "delete"
    owner_id: int     # User's Strava ID
    subscription_id: int
    event_time: int
    updates: dict[str, Any] = {} # Changes (e.g., title on update)


class SyncResponce(BaseModel):
    message: str
    synced_count: int


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    strava_id: int
    name: str
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    type: str
    start_date: datetime
    average_speed: float | None = None
    max_speed: float | None = None
    average_heartrate: float | None = None
    max_heartrate: float | None = None
