from datetime import timedelta, datetime, timezone
from typing import Union

import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from app.config import settings
from app.users.dao import UsersDAO
from app.users.models import Users

# Password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password (str): The plain password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a hashed password.

    Args:
        password (str): The plain password.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    Create an access token with an expiration time.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (Union[timedelta, None], optional): The expiration time delta. Defaults to None.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + settings.TOKEN_TIMER
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str) -> Union[Users, None]:
    """
    Authenticate a user by verifying the email and password.

    Args:
        email (EmailStr): The user's email.
        password (str): The plain password.

    Returns:
        Union[Users, None]: The user if authentication is successful, otherwise None.
    """
    user = await UsersDAO.find_one_or_none(email=email)
    if user is None or not verify_password(password, user.password):
        return None
    return user
