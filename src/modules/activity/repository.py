import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from src.domain.entities.activity import Activity
from src.modules.activity.models import ActivityModel


logger = logging.getLogger(__name__)


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_or_update(self, activity: Activity) -> str:
        values = {
            "user_id": str(activity.user_id),
            "strava_id": activity.strava_id,
            "name": activity.name,
            "distance": activity.distance,
            "moving_time": activity.moving_time,
            "elapsed_time": activity.elapsed_time,
            "total_elevation_gain": activity.total_elevation_gain,
            "type": activity.type,
            "start_date": activity.start_date,
            "average_speed": activity.average_speed,
            "max_speed": activity.max_speed,
            "average_heartrate": activity.average_heartrate,
            "max_heartrate": activity.max_heartrate,
            "raw_data": activity.raw_data,
        }

        stmt = insert(ActivityModel).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[ActivityModel.strava_id],
            set_=values                               
        )

        await self.session.execute(stmt)
        await self.session.commit() 
        
        return str(activity.strava_id)

    async def get_all_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> list[Activity]:
        query = (
            select(ActivityModel)
            .where(ActivityModel.user_id == user_id)
            .order_by(ActivityModel.start_date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        activities = result.scalars().all()
        return [self._to_entity(act) for act in activities]

    def _to_entity(self, db_activity: ActivityModel) -> Activity:
        return Activity(
            id=str(db_activity.id),
            user_id=str(db_activity.user_id),
            strava_id=db_activity.strava_id,
            name=db_activity.name,
            distance=db_activity.distance,
            moving_time=db_activity.moving_time,
            elapsed_time=db_activity.elapsed_time,
            total_elevation_gain=db_activity.total_elevation_gain,
            type=db_activity.type,
            start_date=db_activity.start_date,
            average_speed=db_activity.average_speed,
            max_speed=db_activity.max_speed,
            average_heartrate=db_activity.average_heartrate,
            max_heartrate=db_activity.max_heartrate,
            raw_data=db_activity.raw_data or {}
        )
