import enum

from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from app.database import Base
from app.tasks.models import task_performers


class Roles(str, enum.Enum):
    PM = "Project Manager"
    DEV = "Developer"
    QA = "Quality Assurance"


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(Enum(Roles), nullable=True, default=None)

    tasks = relationship("Tasks", secondary=task_performers, back_populates="performers")
