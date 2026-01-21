import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.modules.authorization.service import AuthService
from src.modules.authorization.strava_service import StravaService
from src.modules.authorization.schema import (
    Token,
    UserRegistrationRequest,
    UserResponse,
)
from src.modules.authorization.auth import create_access_token, create_refresh_token, verify_refresh_token
from src.modules.authorization.dependencies import get_auth_service, get_current_user, get_strava_service
from src.domain.entities.user import User


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sign-up")
async def sign_up(
    request: UserRegistrationRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.register(email=request.email, password=request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return {"message": "User registered successfully", "user": user.model_dump()}


@router.post("/sign-in", response_model=Token)
async def sign_in(
    request: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
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
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at
    )


# Strava OAuth Routes

@router.get("/strava/connect")
async def connect_strava(
    current_user: User = Depends(get_current_user),
    strava_service: StravaService = Depends(get_strava_service)
):
    authorization_url = strava_service.generate_authorization_url(current_user.email)
    return {"authorization_url": authorization_url}


@router.get("/strava/sign-up")
async def strava_sign_up(
    strava_service: StravaService = Depends(get_strava_service)
):
    pass


@router.get("/strava/callback")
async def strava_callback(
    code: str,
    state: str,
    scope: str,
    strava_service: StravaService = Depends(get_strava_service)
):
    """
    Handle OAuth callback from Strava.
    Exchanges authorization code for access token and stores credentials.
    """
    try:
        user = await strava_service.handle_callback(code=code, state=state, scope=scope)
        logger.info(f"Strava connected successfully for user: {user.email}")
        
        # In a real application, you might want to redirect to a frontend success page
        return {
            "message": "Strava connected successfully",
            "strava_id": user.strava_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Strava callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while connecting to Strava"
        )


@router.post("/strava/disconnect")
async def disconnect_strava(
    current_user: User = Depends(get_current_user),
    strava_service: StravaService = Depends(get_strava_service)
):
    await strava_service.disconnect_strava(current_user)
    return {"message": "Strava disconnected successfully"}


@router.get("/strava/profile")
async def get_strava_profile(
    current_user: User = Depends(get_current_user),
    strava_service: StravaService = Depends(get_strava_service)
):
    if not current_user.strava_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Strava not connected. Please connect your Strava account first."
        )
    
    profile = await strava_service.get_athlete_profile(current_user)
    return profile
