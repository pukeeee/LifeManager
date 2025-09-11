from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

from app.core.utils.config import DB_URL

# Створюємо двигун з правильними налаштуваннями
engine = create_async_engine(
    url=DB_URL,
    echo=False,
    pool_pre_ping=True
)

# Створюємо фабрику сесій
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key = True)
    tg_id = mapped_column(BigInteger)
    experience: Mapped[int] = mapped_column(BigInteger, default = 0)
    all_tasks_count: Mapped[int] = mapped_column(Integer, default = 0)
    all_habits_count: Mapped[int] = mapped_column(Integer, default = 0)
    start_date: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default = True)
    user_name: Mapped[str] = mapped_column(String(25), nullable=True)
    avatar: Mapped[str] = mapped_column(String(30), nullable=True)




class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key = True)
    task: Mapped[str] = mapped_column(String(100))
    user: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[bool] = mapped_column(Boolean, default = False)
    done_date: Mapped[int] = mapped_column(Integer, default = 0)
    experience_points: Mapped[int] = mapped_column(Integer, nullable = False)
    complexity: Mapped[str] = mapped_column(String(5), nullable = False)



class Habit(Base):
    __tablename__ = "habits"
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str] = mapped_column(String(100), nullable = False)
    days_of_week: Mapped[str] = mapped_column(String(7), nullable = False)
    status: Mapped[bool] = mapped_column(Boolean, default = False)
    created_date: Mapped[int] = mapped_column(Integer)
    experience_points: Mapped[int] = mapped_column(Integer, nullable = False)
    complexity: Mapped[str] = mapped_column(String(5), nullable = False)



class Statistic(Base):
    __tablename__ = "statistics"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[int] = mapped_column(Integer)  # мітка часу Unix
    tasks_count: Mapped[int] = mapped_column(Integer, default=0)
    habits_count: Mapped[int] = mapped_column(Integer, default=0)



async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
