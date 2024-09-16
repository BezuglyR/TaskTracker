from sqlalchemy import insert, update, delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions import TaskWasNotUpdatedException, TaskAlreadyExistsException, TaskCreationFailedException
from app.tasks.helpers import prepare_performers_data
from app.tasks.models import Tasks, task_performers


class TasksDAO(BaseDAO):
    model = Tasks

    @classmethod
    async def add_task_and_performers(cls, **data) -> Tasks:
        """
        Adds a new task along with performers.
        Inserts a new task into the database, and if performers are provided,
        it associates them with the task.

        Args:
            data: Dictionary with task details and performers.

        Returns:
            Task object with related performers.

        Raises:
            Any relevant SQLAlchemy exceptions during transaction.
        """
        performers = data.pop(cls.model.performers.key, None)

        async with async_session_maker() as session:
            try:
                # Step 1: Insert the new task into the database and get the new task ID
                query = insert(cls.model).values(**data).returning(cls.model.id)
                result = await session.execute(query)
                new_task_id = result.fetchone()[0]

                # Step 2: If performers are provided, associate them with the new task
                if performers:
                    performers_data = await prepare_performers_data(new_task_id, performers)
                    query = insert(task_performers).values(*performers_data)
                    await session.execute(query)

                # Step 3: Commit the transaction and return the new task with its performers
                await session.commit()
                return await cls.find_task_by_id_join_performers(new_task_id)

            except IntegrityError as e:
                await session.rollback()
                # Check if the error is related to unique constraint violation
                if 'unique constraint' in str(e.orig):
                    raise TaskAlreadyExistsException

            except Exception:
                await session.rollback()
                raise TaskCreationFailedException

    @classmethod
    async def update_task_and_performers(cls, task_id: int, **data) -> Tasks:
        """
        Updates an existing task and its performers.
        Updates the task data and replaces the performers linked to the task.

        Args:
            task_id (int): ID of the task to be updated.
            data: Dictionary with updated task details and performers.

        Returns:
            Updated task object with related performers.

        Raises:
            TaskWasNotUpdatedException: If the task with the given ID does not exist.
            Any relevant SQLAlchemy exceptions during transaction.
        """
        performers = data.pop(cls.model.performers.key, [])
        result_data = {k: v for k, v in data.items() if v}  # Remove empty fields

        async with async_session_maker() as session:
            try:
                # Step 1: Update the task data
                query = (
                    update(cls.model)
                    .where(cls.model.id == task_id)
                    .values(**result_data)
                    .returning(cls.model)
                )
                updated_task = await session.execute(query)

                # Check if the task was actually updated (if task_id exists)
                if updated_task.fetchone() is None:
                    raise TaskWasNotUpdatedException

                # Step 2: Update the performers
                if performers:
                    # Delete current performers for the task
                    delete_query = delete(task_performers).where(task_performers.c.task_id == task_id)
                    await session.execute(delete_query)

                    # Insert new performers if provided
                    performers_data = await prepare_performers_data(task_id, performers)
                    insert_query = insert(task_performers).values(performers_data)
                    await session.execute(insert_query)

                # Step 3: Commit the transaction and return the updated task
                await session.commit()
                return await cls.find_task_by_id_join_performers(task_id)

            except TaskWasNotUpdatedException:
                await session.rollback()
                raise TaskWasNotUpdatedException("Task with given ID was not found for update.")

            except Exception:
                await session.rollback()
                raise TaskWasNotUpdatedException

    @classmethod
    async def find_task_by_id_join_performers(cls, task_id: int):
        """
        Finds a task by its ID, including its performers.

        Args:
            task_id (int): ID of the task to be fetched.

        Returns:
            Task object with its related performers if found, else None.
        """
        async with async_session_maker() as session:
            try:
                # Step 1: Select the task and its associated performers using joinedload
                query = select(cls.model).options(joinedload(cls.model.performers)).filter_by(id=task_id)
                result = await session.execute(query)
                return result.unique().scalar_one_or_none()

            except Exception:
                raise TaskWasNotUpdatedException
