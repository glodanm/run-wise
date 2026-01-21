from typing import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.container import Container
from src.core.database import get_db_session
from src.domain.entities.user import User
from src.modules.authorization.auth import verify_access_key
from src.modules.authorization.repository import UserRepository
from src.modules.authorization.service import AuthService
from src.modules.authorization.strava_service import StravaService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/sign-in")


@inject
async def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[..., UserRepository] = Depends(Provide[Container.user_repository.provider]),
    service_factory: Callable[..., AuthService] = Depends(Provide[Container.auth_service.provider]),
) -> AuthService:
    repository = repo_factory(session=session)
    return service_factory(repository=repository)


@inject
async def get_strava_service(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[..., UserRepository] = Depends(Provide[Container.user_repository.provider]),
    service_factory: Callable[..., StravaService] = Depends(Provide[Container.strava_service.provider]),
) -> StravaService:
    repository = repo_factory(session=session)
    return service_factory(repository=repository)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Dependency to get the current authenticated user from JWT token"""
    email = verify_access_key(token)
    
    user = await auth_service.repository.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
