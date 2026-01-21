import uuid

from datetime import datetime, timezone

from sqlalchemy import Column, String, UUID, DateTime, BigInteger

from src.core.database import Base


class UserModel(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Strava integration fields
    strava_id = Column(BigInteger, unique=True, nullable=True, index=True)
    strava_access_token = Column(String, nullable=True)
    strava_refresh_token = Column(String, nullable=True)
    strava_token_expires_at = Column(DateTime(timezone=True), nullable=True)
