import uuid
import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.core.database import Database
from src.domain.entities.user import User
from src.modules.authorization.models import UserModel


logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, database: Database):
        self.database = database

    async def get_by_email(self, email: str) -> User | None:
        async with self.database.async_session() as session:
            query = select(UserModel).where(UserModel.email == email)
            result = await session.execute(query)
            db_user = result.scalar_one_or_none()

            if db_user:
                return User(
                    id=str(db_user.id),
                    email=db_user.email,
                    password=db_user.password
                )
            return None


    async def create(self, user: User) -> str:
        async with self.database.async_session() as session:
            try:
                db_user = UserModel(
                    id=uuid.UUID(user.id),
                    email=user.email,
                    password=user.password
                )
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)
                return str(db_user.id)
            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Database integrity error creating user {user.email}: {e}")
                raise ValueError(f"User with email {user.email} already exists")
