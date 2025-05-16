from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

import os
from dotenv import load_dotenv

load_dotenv()
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')

engine = create_async_engine(url=f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25), nullable=True)
    location: Mapped[str] = mapped_column(String(50), nullable=True)
    language: Mapped[str] = mapped_column(String[10], nullable=True)
    notifies: Mapped[list['Notify']] = relationship(back_populates='user',cascade="all, delete-orphan")


class Notify(Base):
    __tablename__ = 'notifies'
    id: Mapped[int] = mapped_column(primary_key=True)
    hour: Mapped[Integer] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped[User] = relationship(back_populates='notifies')


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
