import logging
from datetime import datetime
from typing import List

from src.domain.entities.user import User
from src.domain.entities.activity import Activity
from src.modules.activity.repository import ActivityRepository
from src.modules.authorization.strava_service import StravaService

logger = logging.getLogger(__name__)

class ActivityService:
    def __init__(self, repository: ActivityRepository, strava_service: StravaService):
        self.repository = repository
        self.strava_service = strava_service

    async def sync_user_activities(self, user: User) -> int:

        logger.info(f"Starting sync for user {user.email}")
        
        strava_activities = await self.strava_service.get_activities(user, limit=50)
        
        count = 0
        for data in strava_activities:
            if data.get("type") != "Run":
                continue

            try:
                activity = Activity(
                    user_id=user.id,
                    strava_id=data["id"],
                    name=data.get("name", "Unknown Run"),
                    distance=data.get("distance", 0.0),
                    moving_time=data.get("moving_time", 0),
                    elapsed_time=data.get("elapsed_time", 0),
                    total_elevation_gain=data.get("total_elevation_gain", 0.0),
                    type=data.get("type"),
                    start_date=datetime.fromisoformat(data["start_date"].replace('Z', '+00:00')),
                    average_speed=data.get("average_speed"),
                    max_speed=data.get("max_speed"),
                    average_heartrate=data.get("average_heartrate"),
                    max_heartrate=data.get("max_heartrate"),
                    raw_data=data,
                )
                
                await self.repository.create_or_update(activity)
                count += 1
                
            except Exception as e:
                logger.error(f"Error saving activity {data.get('id')}: {e}")
                continue

        logger.info(f"Synced {count} activities for user {user.email}")
        return count

    async def get_user_activities(self, user_id: str) -> List[Activity]:
        return await self.repository.get_all_by_user(user_id)
