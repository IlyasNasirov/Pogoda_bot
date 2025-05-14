from models import async_session
from models import User, Notify
from sqlalchemy import select


async def set_user(id, name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == id))
        if not user:
            user = User(id=id, name=name)
            session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def get_user(id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.id == id))


async def set_language(id, lang_code):
    async with async_session() as session:
        exist_user = await session.scalar(select(User).where(User.id == id))
        if exist_user:
            exist_user.language = lang_code
            await session.commit()


async def save_location(id, location):
    async with async_session() as session:
        exist_user = await session.scalar(select(User).where(User.id == id))
        if exist_user:
            exist_user.location = location
            await session.commit()


async def get_notifies(hour):
    async with async_session() as session:
        return await session.scalars(select(Notify).where(Notify.hour == hour))


async def get_notifies_by_user_id(user_id):
    async with async_session() as session:
        return await session.scalars(select(Notify).where(Notify.user_id == user_id))


async def add_notify(user_id, hour):
    async with async_session() as session:
        exist_notify = await session.scalar(select(Notify).where((Notify.hour == hour) & (Notify.user_id == user_id)))
        if not exist_notify:
            session.add(Notify(hour=hour, user_id=user_id))
            await session.commit()


async def delete_notify(user_id, hour):
    async with async_session() as session:
        exist_notify = await session.scalar(select(Notify).where((Notify.hour == hour) & (Notify.user_id == user_id)))
        if exist_notify:
            await session.delete(exist_notify)
            await session.commit()
