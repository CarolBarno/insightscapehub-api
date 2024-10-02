import uuid
from datetime import datetime, timedelta, timezone
from insightscapehub.utils.db import Base
from sqlalchemy import UUID, Column, DateTime, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from insightscapehub.dependencies.host import build_qualified_url
from insightscapehub.utils.enums import VerificationTokenStatus, VerificationType
from insightscapehub.models import User


def get_default_expiry():
    return datetime.now(timezone.utc) + timedelta(minutes=60)


class VerificationToken(Base):
    __tablename__ = 'verification_tokens'

    id = Column(UUID(True), primary_key=True, default=uuid.uuid4)
    type = Column(String, default=VerificationType.INITIAL_VERIFICATION.value)
    status = Column(String, default=VerificationTokenStatus.UNUSED.value)
    token = Column(Text(), nullable=False)
    expiry = Column(DateTime(True), default=get_default_expiry)
    user_id = Column(UUID, ForeignKey(
        User.id, ondelete='CASCADE'), nullable=False)
    host = Column(Text(), nullable=True)
    user = relationship('User', back_populates='verification_tokens')

    @property
    def auth_link(self):
        if not self.host:
            return self.token

        qualified = build_qualified_url(
            self.host, f'auth/verify/{self.token}/')

        return qualified

    @property
    def is_expired(self):
        expiry = self.expiry
        if expiry and expiry < datetime.now(tz=timezone.utc):
            return True
        return False

    @property
    def can_resend(self):
        if self.status != VerificationTokenStatus.USED.value:
            return True

        return False

    @property
    def remaining_minutes(self):
        if not self.expiry:
            return 0

        now = datetime.now(tz=timezone.utc)

        difference_in_minutes = int((self.expiry - now).total_seconds() / 60)

        return difference_in_minutes

    @property
    def is_used(self):
        return self.status == VerificationTokenStatus.USED.value

    def __repr__(self):
        return f'{self.type} :> {self.token}'
