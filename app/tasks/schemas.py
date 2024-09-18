from datetime import datetime
from typing import Optional, List, Union

from fastapi import Form
from pydantic import BaseModel, Field, validator, field_validator

from app.tasks.models import TaskStatus, TaskPriority
from app.users.schemas import SUsersResponse


class STasksCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=10, max_length=255)
    status: TaskStatus
    priority: TaskPriority
    responsible_user_id: int = Field(gt=0)
    performers: list[int] | list[str] = []

    class Config:
        from_attributes = True

    @field_validator('performers', mode='before')
    def validate_performers(cls, v):
        if isinstance(v, list):
            performers_list = [
                int(p.strip()) for item in v for p in item.split(',')
                if p.strip().isdigit()
            ]
            if any(p == 0 for p in performers_list):
                raise ValueError("Performer list contains invalid value: 0.")
            return performers_list

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
    title: str = None
    description: str = None
    status: Optional[TaskStatus]
    priority: Optional[TaskPriority]
    responsible_user_id: int = 0
    performers: list[int] | list[str] = None


class STasksStatusUpdate(BaseModel):
    status: TaskStatus

    class Config:
        from_attributes = True
