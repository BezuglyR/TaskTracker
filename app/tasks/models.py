import enum
import datetime

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Index, DateTime, Table, func
from sqlalchemy.orm import relationship

from app.database import Base


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "In progress"
    COMPLETED = "Done"


class TaskPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


task_performers = Table(
    'task_performers',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id', ondelete="CASCADE")),
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"))
)


class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    description = Column(String)
    responsible_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    performers = relationship("Users", secondary=task_performers, back_populates="tasks")
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_tasks_status_priority', 'status', 'priority'),
    )
