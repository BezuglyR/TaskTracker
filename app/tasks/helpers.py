from typing import List, Optional

from pydantic import parse_obj_as

from app.tasks.models import Tasks
from app.tasks.schemas import STasksResponse
from app.users.dao import UsersDAO


async def add_responsible_and_performers_users_models_in_task_response(
        task: Tasks,
        performers_list: Optional[List[int]] = None
) -> STasksResponse:
    """Add responsible user and performers to the task response.

    Args:
        task (Tasks): The task object to be updated.
        performers_list (Optional[List[int]]): List of performer user IDs.

    Returns:
        STasksResponse: The task with updated user details.
    """
    # Retrieve the responsible user
    responsible_user = await UsersDAO.find_by_id(task.responsible_user_id)

    # Retrieve the performers if provided
    if performers_list:
        performers_list = await UsersDAO.find_all(id=performers_list) or []
    else:
        performers_list = []

    # Update the task with user details
    task.responsible_user = responsible_user
    task.performers = performers_list

    # Convert the task object to the response schema
    result = parse_obj_as(STasksResponse, task)

    return result


async def prepare_performers_data(
        task_id: int,
        performers_list: List[int]
) -> List[dict]:
    """Prepare the data for performers.

    Args:
        task_id (int): The ID of the task.
        performers_list (List[int]): List of performer user IDs.

    Returns:
        List[dict]: List of dictionaries containing task ID and performer user IDs.
    """
    if not performers_list:
        return []

    # Prepare the performers data
    performers_data = [
        {'task_id': task_id, 'user_id': performer_id}
        for performer_id in performers_list
    ]

    return performers_data
