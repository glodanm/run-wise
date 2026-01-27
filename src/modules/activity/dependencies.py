from typing import Callable
from fastapi import Depends
from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.container import Container
from src.core.database import get_db_session
from src.modules.activity.repository import ActivityRepository
from src.modules.activity.service import ActivityService
from src.modules.authorization.dependencies import get_strava_service
from src.modules.authorization.strava_service import StravaService


@inject
async def get_activity_service(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[..., ActivityRepository] = Depends(Provide[Container.activity_repository.provider]),
    service_factory: Callable[..., ActivityService] = Depends(Provide[Container.activity_service.provider]),
    strava_service: StravaService = Depends(get_strava_service),
) -> ActivityService:
    repository = repo_factory(session=session)
    return service_factory(repository=repository, strava_service=strava_service)
