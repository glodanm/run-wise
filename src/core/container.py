import logging

from dependency_injector import containers, providers

from src.modules.activity.repository import ActivityRepository
from src.modules.activity.service import ActivityService
from src.modules.authorization.repository import UserRepository
from src.modules.authorization.service import AuthService
from src.modules.authorization.strava_service import StravaService


from .config import Configurations
from .database import Database

logger = logging.getLogger(__name__)

class Container(containers.DeclarativeContainer):

    config = providers.Singleton(Configurations)

    database = providers.Singleton(Database, config=config)

    user_repository = providers.Factory(
        UserRepository,
    )

    auth_service = providers.Factory(
        AuthService,
    )
    
    strava_service = providers.Factory(
        StravaService,
        config=config,
    )

    activity_repository = providers.Factory(
        ActivityRepository,
    )

    activity_service = providers.Factory(
        ActivityService,
    )
