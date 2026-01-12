import logging

from dependency_injector import containers, providers


from .config import Configurations
from .database import Database

logger = logging.getLogger(__name__)

class Container(containers.DeclarativeContainer):

    config = providers.Singleton(Configurations)

    database = providers.Singleton(Database, config=config)

    