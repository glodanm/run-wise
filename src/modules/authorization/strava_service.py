import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict

import httpx
from fastapi import HTTPException, status

from src.core.config import Configurations
from src.modules.authorization.repository import UserRepository
from src.domain.entities.user import User

logger = logging.getLogger(__name__)


class StravaService:
    """Service for handling Strava OAuth2 authentication and token management"""
    
    STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
    STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
    STRAVA_API_URL = "https://www.strava.com/api/v3"
    
    # In-memory storage for state tokens (use Redis in production)
    _state_storage: Dict[str, str] = {}
    
    def __init__(self, config: Configurations, repository: UserRepository):
        self.config = config
        self.repository = repository
        self.client_id = config.STRAVA_CLIENT_ID
        self.client_secret = config.STRAVA_CLIENT_SECRET
        self.redirect_uri = config.STRAVA_REDIRECT_URI
    
    def generate_authorization_url(self, user_email: str) -> str:
        """
        Generate Strava OAuth authorization URL
        
        Args:
            user_email: Email of the user initiating the connection
            
        Returns:
            Authorization URL to redirect the user to
        """
        state = secrets.token_urlsafe(32)
        self._state_storage[state] = user_email
        
        auth_url = (
            f"{self.STRAVA_AUTH_URL}?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"scope=read,activity:read_all,profile:read_all&"
            f"state={state}"
        )
        
        logger.info(f"Generated Strava authorization URL for user: {user_email}")
        return auth_url
    
    async def handle_callback(self, code: str, state: str, scope: str) -> User:
        """
        Handle OAuth callback from Strava
        
        Args:
            code: Authorization code from Strava
            state: State token for CSRF validation
            scope: Scopes granted by user
            
        Returns:
            Updated user object with Strava credentials
            
        Raises:
            HTTPException: If state is invalid or token exchange fails
        """
        user_email = self._state_storage.get(state)
        if not user_email:
            logger.error(f"Invalid state token: {state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter. Please try connecting again."
            )
        
        del self._state_storage[state]
        
        user = await self.repository.get_by_email(user_email)
        if not user:
            logger.error(f"User not found for email: {user_email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        try:
            token_data = await self._exchange_code_for_token(code)
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to connect to Strava. Please try again."
            )
        
        expires_at = datetime.fromtimestamp(token_data["expires_at"], tz=timezone.utc)
        
        updated_user = await self.repository.update_strava_credentials(
            user_id=user.id,
            strava_id=token_data["athlete"]["id"],
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_at=expires_at
        )
        
        logger.info(f"Successfully connected Strava for user: {user_email}")
        return updated_user
    
    async def _exchange_code_for_token(self, code: str) -> dict:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from Strava
            
        Returns:
            Token response from Strava API
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.STRAVA_TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Strava token exchange failed: {response.text}")
                raise Exception(f"Token exchange failed: {response.text}")
            
            return response.json()
    
    async def refresh_access_token(self, user: User) -> User:
        """
        Refresh expired Strava access token
        
        Args:
            user: User with expired token
            
        Returns:
            Updated user with new token
        """
        if not user.strava_refresh_token:
            logger.error(f"No refresh token available for user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Strava refresh token available"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.STRAVA_TOKEN_URL,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": user.strava_refresh_token,
                        "grant_type": "refresh_token"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Token refresh failed: {response.text}")
                    raise Exception(f"Token refresh failed: {response.text}")
                
                token_data = response.json()
                expires_at = datetime.fromtimestamp(token_data["expires_at"], tz=timezone.utc)
                
                updated_user = await self.repository.update_strava_credentials(
                    user_id=user.id,
                    strava_id=user.strava_id,
                    access_token=token_data["access_token"],
                    refresh_token=token_data["refresh_token"],
                    expires_at=expires_at
                )
                
                logger.info(f"Successfully refreshed token for user: {user.email}")
                return updated_user
                
        except Exception as e:
            logger.error(f"Failed to refresh token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to refresh Strava token"
            )
    
    async def get_valid_access_token(self, user: User) -> str:
        """
        Get a valid access token, refreshing if necessary
        
        Args:
            user: User to get token for
            
        Returns:
            Valid access token
        """
        if not user.strava_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not connected to Strava"
            )

        now = datetime.now(timezone.utc)
        if user.strava_token_expires_at and user.strava_token_expires_at <= now + timedelta(minutes=5):
            logger.info(f"Token expired for user {user.email}, refreshing...")
            user = await self.refresh_access_token(user)
        
        return user.strava_access_token
    
    async def disconnect_strava(self, user: User) -> User:
        """
        Disconnect user's Strava account
        
        Args:
            user: User to disconnect
            
        Returns:
            Updated user with cleared Strava credentials
        """
        updated_user = await self.repository.update_strava_credentials(
            user_id=user.id,
            strava_id=None,
            access_token=None,
            refresh_token=None,
            expires_at=None
        )
        
        logger.info(f"Disconnected Strava for user: {user.email}")
        return updated_user
    
    async def get_athlete_profile(self, user: User) -> dict:
        """
        Get athlete profile from Strava API
        
        Args:
            user: User with Strava connection
            
        Returns:
            Athlete profile data
        """
        access_token = await self.get_valid_access_token(user)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.STRAVA_API_URL}/athlete",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get athlete profile: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get Strava profile"
                )
            
            return response.json()
    
    async def get_activities(self, user: User, limit: int = 10) -> list[dict]:
        access_token = await self.get_valid_access_token(user)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.STRAVA_API_URL}/athlete/activities",
                params={"per_page": limit},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch activities: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch activities from Strava"
                )
            
            return response.json()
