import logging

from dependency_injector import containers, providers

from src.modules.authorization.repository import UserRepository
from src.modules.authorization.service import AuthService


from .config import Configurations
from .database import Database

logger = logging.getLogger(__name__)

class Container(containers.DeclarativeContainer):

    config = providers.Singleton(Configurations)

    database = providers.Singleton(Database, config=config)

    user_repository = providers.Factory(
        UserRepository,
        database=database
    )

    auth_service = providers.Factory(
        AuthService,
        repository=user_repository
    )
