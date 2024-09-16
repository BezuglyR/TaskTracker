import datetime
from typing import Annotated

import jwt
from fastapi import Request, Depends
from jwt import InvalidTokenError

from app.config import settings
from app.exceptions import (
    UserNotAuthorizeException,
    NoAccessRightsException,
    TokenExpiredException,
    TokenNotFoundException,
    UserNotExistsException
)
from app.tasks.dao import TasksDAO
from app.tasks.models import Tasks
from app.users.dao import UsersDAO
from app.users.models import Users, Roles


def get_token(request: Request) -> str:
    """
    Extract the JWT token from the request cookies.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        str: The JWT token.

    Raises:
        TokenNotFoundException: If the token is not found in the cookies.
    """
    token = request.cookies.get(settings.TOKEN_NAME)
    if not token:
        raise TokenNotFoundException
    return token


async def get_current_user(token: str = Depends(get_token)) -> Users:
    """
    Retrieve the current user from the token.

    Args:
        token (str): The JWT token.

    Returns:
        Users: The authenticated user.

    Raises:
        UserNotAuthorizeException: If the token is invalid or expired.
        TokenExpiredException: If the token is expired.
        UserNotExistsException: If the user does not exist in the database.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise UserNotAuthorizeException
    except InvalidTokenError:
        raise UserNotAuthorizeException

    expire: str = payload.get("exp")
    if expire is None or int(expire) < datetime.datetime.now(datetime.timezone.utc).timestamp():
        raise TokenExpiredException

    user: Users = await UsersDAO.find_by_id(int(username))
    if user is None:
        raise UserNotExistsException

    return user


async def get_current_pm_user(current_user: Annotated[Users, Depends(get_current_user)]) -> Users:
    """
    Ensure the current user is a Project Manager (PM).

    Args:
        current_user (Users): The current user.

    Returns:
        Users: The current user if they are a PM.

    Raises:
        NoAccessRightsException: If the user is not a PM.
    """
    if current_user.role != Roles.PM:
        raise NoAccessRightsException
    return current_user


async def get_pm_and_responsible_user(
        task_id: int,
        current_user: Annotated[Users, Depends(get_current_user)]
) -> Users:
    """
    Ensure the current user is either the responsible user or a Project Manager (PM) for a task.

    Args:
        task_id (int): The ID of the task.
        current_user (Users): The current user.

    Returns:
        Users: The current user if they have the required access rights.

    Raises:
        NoAccessRightsException: If the user does not have the required access rights.
    """
    task: Tasks = await TasksDAO.find_by_id(task_id)
    if task.responsible_user_id != current_user.id and current_user.role != Roles.PM:
        raise NoAccessRightsException
    return current_user


async def get_pm_and_responsible_and_performers_user(
        task_id: int,
        current_user: Annotated[Users, Depends(get_current_user)]
) -> Users:
    """
    Ensure the current user is either the responsible user, a Project Manager (PM), or a performer for a task.

    Args:
        task_id (int): The ID of the task.
        current_user (Users): The current user.

    Returns:
        Users: The current user if they have the required access rights.

    Raises:
        NoAccessRightsException: If the user does not have the required access rights.
    """
    task: Tasks = await TasksDAO.find_task_by_id_join_performers(task_id)
    performers = [performer.id for performer in task.performers]
    if (task.responsible_user_id != current_user.id and
            current_user.role != Roles.PM and
            current_user.id not in performers):
        raise NoAccessRightsException
    return current_user
