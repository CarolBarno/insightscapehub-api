import uuid
from insightscapehub.utils.db import Base
from sqlalchemy import UUID, Column, String

class Users(Base):
    __tablename__ = 'users'

    id = Column(UUID(True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    _password = Column(String(100), nullable=True)

    @property
    def password(self):
        raise ValueError('Cannot access this value directly')
    
    @password.setter
    def _set_password(self, _):
        raise ValueError('Cannot set password value directly')
    
    def set_password(self, password: str) -> None:
        from ..security.hashing import get_password_hash

        self._password = get_password_hash(password)

        return self
    
    def check_password(self, password: str) -> bool:
        if not self._password:
            return False
        
        from ..security.hashing import verify_password

        return verify_password(password, self._password)


