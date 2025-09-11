from sqlalchemy.ext.asyncio import AsyncSession
from database.models import async_session
from contextlib import asynccontextmanager


class BaseRepository:
    """
    Базовий клас-репозиторій для роботи з асинхронними сесіями SQLAlchemy.
    Дозволяє автоматично керувати сесією та транзакціями.
    """
    
    
    def __init__(self):
        """
        Ініціалізує об'єкт, але не створює сесію відразу.
        """
        self._session: AsyncSession | None = None  # Змінна для зберігання сесії
        self._transaction_in_progress: bool = False  # Прапорець для відстеження стану транзакції
    
    
    async def __aenter__(self):
        """
        Асинхронний контекстний менеджер для роботи з сесією.
        Використання: `async with BaseRepository() as repo:`
        """
        self._session = async_session()  # Створення нової сесії
        return self  # Повертає сам об'єкт, щоб можна було звертатися до `self.session`
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Закриття сесії при виході з контекстного менеджера.
        Якщо сталася помилка (exc_type != None), виконується відкат змін (rollback).
        Якщо помилок немає, виконується коміт (commit).
        """
        if self._session:
            try:
                if exc_type:
                    await self._session.rollback()  # Відкат, якщо була помилка
                else:
                    await self._session.commit()  # Фіксуємо зміни в БД
            finally:
                await self._session.close()  # Закриваємо сесію після роботи
                self._session = None  # Очищаємо змінну
                self._transaction_in_progress = False  # Скидаємо прапорець транзакції
    
    
    
    @property
    def session(self) -> AsyncSession:
        """
        Властивість для отримання поточної сесії.
        Якщо сесія не ініціалізована, викидається помилка.
        """
        if not self._session:
            raise RuntimeError("Session not initialized. Use 'async with' context")  
        return self._session  # Повертаємо сесію, якщо вона активна
    
    
    
    @asynccontextmanager
    async def begin(self):
        """
        Контекстний менеджер для роботи з транзакціями.
        Дозволяє використовувати `async with repo.begin():`, щоб вручну керувати транзакціями.
        """
        if not self._session:
            raise RuntimeError("Session not initialized")  # Перевірка на наявність сесії
        
        if not self._transaction_in_progress:
            self._transaction_in_progress = True  # Встановлюємо прапорець початку транзакції
            async with self._session.begin() as transaction:  # Починаємо транзакцію
                try:
                    yield  # Виконуємо код усередині `async with repo.begin():`
                except Exception:
                    await transaction.rollback()  # У разі помилки робимо відкат
                    raise  # Прокидаємо виняток далі
                finally:
                    self._transaction_in_progress = False  # Скидаємо прапорець транзакції
        else:
            yield  # Якщо транзакція вже запущена, продовжуємо її використовувати без створення нової