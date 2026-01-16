from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dependency_injector.wiring import inject, Provide

from src.core.container import Container
from src.domain.entities.user import User
from src.modules.authorization.auth import verify_access_key
from src.modules.authorization.service import AuthService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/sign-in")


@inject
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(Provide[Container.auth_service])
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


