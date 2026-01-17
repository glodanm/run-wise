import uuid
import bcrypt

from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """Domain entity користувача"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), frozen=True)
    email: EmailStr
    password: str 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def create_with_password(cls, email: str, password: str, **kwargs) -> "User":
        """Створити користувача з паролем (автоматично хешується)"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return cls(email=email, password=hashed.decode('utf-8'), **kwargs)
    
    def check_password(self, password: str) -> bool:
        """Перевірити пароль"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password.encode('utf-8')
        )
