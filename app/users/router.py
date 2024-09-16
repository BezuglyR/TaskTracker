from typing import Annotated

from fastapi import APIRouter, Form, Depends, Response

from app.config import settings
from app.exceptions import (
    EmailOrPasswordIncorrectException,
    UserAlreadyExistsException
)
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.users.schemas import SUsersRegister, SUsersLogin, SUsersResponse

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=SUsersResponse)
async def register_user(user_data: Annotated[SUsersRegister, Form()]):
    """
    Register a new user.

    Args:
        user_data (SUsersRegister): The user registration data.

    Returns:
        SUsersResponse: The registered user data.

    Raises:
        UserAlreadyExistsException: If the user with the given email already exists.
    """
    existing_user = await UsersDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistsException

    hashed_password = get_password_hash(user_data.password)
    new_user = await UsersDAO.create(
        name=user_data.name,
        surname=user_data.surname,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role
    )
    return new_user


@router.post("/login")
async def login_user(response: Response, user_data: Annotated[SUsersLogin, Form()]):
    """
    Authenticate a user and issue a JWT token.

    Args:
        response (Response): The HTTP response object.
        user_data (SUsersLogin): The user login data.

    Returns:
        dict: A dictionary containing the access token.

    Raises:
        EmailOrPasswordIncorrectException: If the email or password is incorrect.
    """
    user = await authenticate_user(email=user_data.email, password=user_data.password)
    if not user:
        raise EmailOrPasswordIncorrectException

    access_token = create_access_token({'sub': user.id})
    response.set_cookie(settings.TOKEN_NAME, access_token, httponly=True)
    return {"access_token": access_token}


@router.post("/logout")
async def logout_user(response: Response):
    """
    Log out the user by deleting the JWT token from cookies.

    Args:
        response (Response): The HTTP response object.
    """
    response.delete_cookie(settings.TOKEN_NAME)


@router.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)):
    """
    Get the details of the currently authenticated user.

    Args:
        current_user (Users): The currently authenticated user.

    Returns:
        Users: The details of the currently authenticated user.
    """
    return current_user
