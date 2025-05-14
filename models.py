from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import Column, Integer, String, ForeignKey
import asyncio

engine = create_async_engine("sqlite+aiosqlite:///./weather.db", echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    language = Column(String)
    notifies = relationship('Notify', back_populates='user')


class Notify(Base):
    __tablename__ = 'notifies'
    id = Column(Integer, primary_key=True)
    hour = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='notifies')


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
