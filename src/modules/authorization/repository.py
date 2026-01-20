import uuid
import logging

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

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

            return self._to_entity(db_user) if db_user else None


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
    
    async def update_strava_credentials(
        self, 
        user_id: str, 
        strava_id: int | None,
        access_token: str | None,
        refresh_token: str | None,
        expires_at: datetime | None
    ) -> User:
        """Update user's Strava OAuth credentials"""
        async with self.database.async_session() as session:
            query = select(UserModel).where(UserModel.id == uuid.UUID(user_id))
            result = await session.execute(query)
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                raise ValueError(f"User with id {user_id} not found")
            
            db_user.strava_id = strava_id
            db_user.strava_access_token = access_token
            db_user.strava_refresh_token = refresh_token
            db_user.strava_token_expires_at = expires_at
            
            await session.commit()
            await session.refresh(db_user)
            
            return self._to_entity(db_user)

    def _to_entity(self, db_user: UserModel) -> User:
        return User(
            id=str(db_user.id),
            email=db_user.email,
            password=db_user.password,
            created_at=db_user.created_at,
            strava_id=db_user.strava_id,
            strava_access_token=db_user.strava_access_token,
            strava_refresh_token=db_user.strava_refresh_token,
            strava_token_expires_at=db_user.strava_token_expires_at,
        )
