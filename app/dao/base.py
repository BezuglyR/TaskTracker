from sqlalchemy import select, insert, delete, update

from app.database import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            base = select(cls.model)

            for key, value in filter_by.items():
                if isinstance(value, list):
                    base = base.filter(getattr(cls.model, key).in_(value))
                else:
                    base = base.filter_by(**{key: value})

            result = await session.execute(base)
            return result.scalars().all()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def create(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model)
            new = await session.execute(query)
            await session.commit()
            return new.scalar()

    @classmethod
    async def delete(cls, model_id: int):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(id=model_id)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update(cls, model_id: int, data: dict):
        async with async_session_maker() as session:
            query = (
                update(cls.model)
                .where(cls.model.id == model_id)
                .values(**data)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()

            return await cls.find_by_id(model_id)  # Return the updated task
