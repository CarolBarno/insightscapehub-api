import re
from typing import Tuple, Union

USERNAME_REGEX = r"^([a-zA-Z])([a-zA-Z0-9-_])*(?<![-.])$"
MIN_PASSWORD_LENGTH = 6
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{%s,}$" % (
    MIN_PASSWORD_LENGTH)
PASSWORD_DESCRIPTION = f"""
Match: {USERNAME_REGEX}
Must be at least {MIN_PASSWORD_LENGTH} characters long.
Must contain at least one uppercase letter (A-Z).
Must contain at least one lowercase letter (a-z).
Must contain at least one digit (0-9).
"""


def is_valid_username_regex(username: str):
    return re.match(USERNAME_REGEX, username) is not None


def is_valid_password(password: str, silent=False) -> Tuple[bool, Union[str, None]]:
    msg: Union[str, None] = None

    if len(password or "") < MIN_PASSWORD_LENGTH:
        msg = f"Password must be atleast {MIN_PASSWORD_LENGTH} characters"
    elif not re.match(PASSWORD_REGEX, password):
        msg = "Password must contain one uppercase letter(A-Z), one lowercase letter (a-z) and atleast one digit (0-9)."

    if msg and not silent:
        raise ValueError(msg)

    return [msg == None, msg]
