from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Configurations
from src.domain.entities.user import User


class UserRepository:
    def __init__(self, session: AsyncSession, config: Configurations):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        pass

    async def create(self, user: User) -> str | None:
        pass
