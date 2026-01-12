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
            logger.info(f"There is no user with email: {email}")
            return None
        if not user.check_password(password):
            return None
        
        return user 
    
    async def register(self, email: str, password: str) -> User | None:
        existing_user = await self.repository.get_by_email(email)
        
        if existing_user:
            logger.info(f"User with email: {email} already exist")
        
        user = User.create_with_password(email=email, password=password)
        await self.repository.create(user)
        
        return user
