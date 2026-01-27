import logging

from fastapi import APIRouter, status, Depends

from src.domain.entities.user import User
from src.modules.activity.dependencies import get_activity_service
from src.modules.activity.schema import SyncResponce, ActivityResponse
from src.modules.activity.service import ActivityService
from src.modules.authorization.dependencies import get_current_user


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/sync", response_model=SyncResponce, status_code=status.HTTP_200_OK)
async def sync_activities(
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service)
):
    count = await activity_service.sync_user_activities(current_user)
    return {"message": "Activities synced successfully", "synced_count": count}


@router.get("/", response_model=list[ActivityResponse])
async def get_my_activities(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service)
):
    activities = await activity_service.get_user_activities(
        user_id=current_user.id
    )
    return activities
