import enum
from typing import List, Union


class Enum(str, enum.Enum):
    @classmethod
    def values(cls) -> List[str]:
        return list(map(lambda c: c.value, cls))


class APITags(Enum):
    user = "Authentication"


class AppsEnum(Enum):
    BASE = 'Base'


class AppPrefixes(Enum):
    BASE = '/api'


def stringify(perm: Union['Enum', str]) -> str:
    if isinstance(perm, str) or not perm:
        return perm

    return getattr(perm, 'value', perm)


class Status(Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class VerificationTokenStatus(Enum):
    UNUSED = "UNUSED"
    USED = "USED"
    FACED_OUT = "FACED_OUT"


class VerificationType(Enum):
    INITIAL_VERIFICATION = "INITIAL_VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"
