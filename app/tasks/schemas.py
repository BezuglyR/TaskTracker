from datetime import datetime
from typing import Optional, List, Union

from fastapi import Form
from pydantic import BaseModel, Field, validator, field_validator

from app.tasks.models import TaskStatus, TaskPriority
from app.users.schemas import SUsersResponse


class STasksCreate(BaseModel):
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    responsible_user_id: int
    performers: Optional[Union[List[int], List[str]]] = None

    class Config:
        from_attributes = True

    @field_validator('performers', mode='before')
    def validate_performers(cls, v):
        if isinstance(v, list):
            return [
                int(p.strip()) for item in v for p in item.split(',')
                if p.strip().isdigit()
            ]

        # Raise an error if the value is of an unexpected type
        raise ValueError('Invalid type for performers field.')


class STasksResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    responsible_user: SUsersResponse
    performers: List[SUsersResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class STasksUpdate(STasksCreate):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus]
    priority: Optional[TaskPriority]
    responsible_user_id: Optional[int] = 0
    performers: Optional[Union[List[int], List[str]]] = None


class STasksStatusUpdate(BaseModel):
    status: TaskStatus

    class Config:
        from_attributes = True
