import logging

from src.domain.entities.user import User
from src.modules.authorization.repository import UserRepository


logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    
    async def login(self, email: str, password: str) -> User | None:
        user = await self.repository.get_by_email(email)
        
        if user is None:
            logger.warning(f"Login attempt failed: no user with email {email}")
            return None
        
        if not user.check_password(password):
            logger.warning(f"Login attempt failed: invalid password for {email}")
            return None
        
        logger.info(f"User {email} logged in successfully")
        return user 
    
    async def register(self, email: str, password: str) -> User | None:
        existing_user = await self.repository.get_by_email(email)
        
        if existing_user:
            logger.info(f"Registration failed: user with email {email} already exists")
            return None
        
        user = User.create_with_password(email=email, password=password)
        await self.repository.create(user)
        logger.info(f"User {email} registered successfully")
        
        return user
