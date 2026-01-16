import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from dependency_injector.wiring import Provide, inject

from src.core.container import Container
from src.modules.authorization.service import AuthService
from src.modules.authorization.schema import (
    Token,
    UserRegistrationRequest,
    UserResponse,
)
from src.modules.authorization.auth import create_access_token, create_refresh_token, verify_refresh_token
from src.modules.authorization.dependencies import get_current_user
from src.domain.entities.user import User


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sign-up")
@inject
async def sign_up(
    request: UserRegistrationRequest, 
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    user = await auth_service.register(email=request.email, password=request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return {"message": "User registered successfully", "user": user.model_dump()}


@router.post("/sign-in", response_model=Token)
@inject
async def sign_in(
    request: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    user = await auth_service.login(email=request.username, password=request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW=Authenticate": "Bearer"},
        )
    
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    email = verify_refresh_token(refresh_token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    new_access_token = create_access_token({"sub": email})
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/users/me", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at
    )
