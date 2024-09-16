from typing import Annotated, List

from fastapi import APIRouter, Depends, Form
from pydantic import parse_obj_as

from app.services.tasks import send_task_update_status_email
from app.tasks.dao import TasksDAO
from app.tasks.helpers import add_responsible_and_performers_users_models_in_task_response
from app.tasks.models import Tasks
from app.tasks.schemas import (
    STasksCreate,
    STasksResponse,
    STasksUpdate,
    STasksStatusUpdate
)
from app.users.dao import UsersDAO
from app.users.dependencies import (
    get_current_user,
    get_current_pm_user,
    get_pm_and_responsible_user,
    get_pm_and_responsible_and_performers_user
)
from app.users.models import Users

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.get("", response_model=List[STasksResponse])
async def get_tasks(
    user: Users = Depends(get_current_user)
):
    """
    Retrieve all tasks.

    Args:
        user (Users): The current user.

    Returns:
        List[STasksResponse]: A list of tasks.
    """
    tasks: List[Tasks] = await TasksDAO.find_all()
    tasks_list = []
    for task in tasks:
        task = await TasksDAO.find_task_by_id_join_performers(task.id)
        task.responsible_user = await UsersDAO.find_by_id(task.responsible_user_id)
        result = parse_obj_as(STasksResponse, task)
        tasks_list.append(result)
    return tasks_list


@router.get("/{task_id}", response_model=STasksResponse)
async def get_task(
    task_id: int,
    user: Users = Depends(get_current_user)
):
    """
    Retrieve a single task by its ID.

    Args:
        task_id (int): The ID of the task.
        user (Users): The current user.

    Returns:
        STasksResponse: The details of the task.
    """
    task = await TasksDAO.find_task_by_id_join_performers(task_id)
    task.responsible_user = await UsersDAO.find_by_id(task.responsible_user_id)
    result = parse_obj_as(STasksResponse, task)
    return result


@router.post("", response_model=STasksResponse)
async def create_task(
    task_data: Annotated[STasksCreate, Form()],
    user: Users = Depends(get_current_pm_user)
):
    """
    Create a new task.

    Args:
        task_data (STasksCreate): The data for the new task.
        user (Users): The current PM user.

    Returns:
        STasksResponse: The created task.
    """
    new_task = await TasksDAO.add_task_and_performers(**task_data.dict())

    result = await add_responsible_and_performers_users_models_in_task_response(
        task=new_task,
        performers_list=task_data.performers
    )
    return result


@router.put("/{task_id}", response_model=STasksResponse)
async def update_task(
    task_id: int,
    task_update_schema: Annotated[STasksUpdate, Form()],
    user: Users = Depends(get_pm_and_responsible_user)
):
    """
    Update an existing task.

    Args:
        task_id (int): The ID of the task.
        task_update_schema (STasksUpdate): The updated task data.
        user (Users): The current PM or responsible user.

    Returns:
        STasksResponse: The updated task.
    """
    task = await TasksDAO.find_by_id(task_id)
    updated_task = await TasksDAO.update_task_and_performers(task_id, **task_update_schema.dict())

    result = await add_responsible_and_performers_users_models_in_task_response(
        task=updated_task
    )

    if task.status != updated_task.status:
        send_task_update_status_email.delay(result.responsible_user.email, result.dict())

    return result


@router.put("/{task_id}/status", response_model=STasksResponse)
async def update_status_task(
    task_id: int,
    task_status_schema: Annotated[STasksStatusUpdate, Form()],
    user: Users = Depends(get_pm_and_responsible_and_performers_user)
):
    """
    Update the status of an existing task.

    Args:
        task_id (int): The ID of the task.
        task_status_schema (STasksStatusUpdate): The updated task status.
        user (Users): The current PM or responsible user.

    Returns:
        STasksResponse: The task with updated status.
    """
    task = await TasksDAO.find_by_id(task_id)
    updated_task = await TasksDAO.update_task_and_performers(task_id, **task_status_schema.dict())

    result = await add_responsible_and_performers_users_models_in_task_response(
        task=updated_task
    )

    if task.status != updated_task.status:
        send_task_update_status_email.delay(result.responsible_user.email, result.dict())

    return result


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    user: Users = Depends(get_current_pm_user)
):
    """
    Delete a task by its ID.

    Args:
        task_id (int): The ID of the task.
        user (Users): The current PM user.
    """
    await TasksDAO.delete(task_id)
