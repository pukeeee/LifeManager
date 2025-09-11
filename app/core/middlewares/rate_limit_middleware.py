from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from redis.asyncio import Redis



class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware для обмеження частоти запитів користувачів.
    Використовує Redis для зберігання загального лічильника запитів.
    """
    def __init__(self, redis_connection: Redis):
        """
        Ініціалізація middleware з підключенням до Redis
        Args:
            redis_connection: Об'єкт підключення до Redis
        """
        self.redis = redis_connection
        
        # Загальні налаштування ліміту для всіх типів запитів
        self.max_requests = 2  # Максимальна кількість запитів
        self.window_seconds = 1  # Часове вікно в секундах
    
    async def check_limit(self, key: str) -> bool:
        """
        Перевіряє, чи не перевищено загальний ліміт запитів для користувача
        
        Args:
            key: Унікальний ключ для користувача
            
        Returns:
            bool: True, якщо запит дозволено, False, якщо ліміт перевищено
        """
        try:
            # Збільшуємо загальний лічильник запитів у Redis
            requests = await self.redis.incr(key)
            
            # Для першого запиту встановлюємо час життя ключа
            if requests == 1:
                # Після закінчення window_seconds ключ буде автоматично видалено
                await self.redis.expire(key, self.window_seconds)
            
            # Дозволяємо запит, якщо лічильник не перевищує ліміт
            return requests <= self.max_requests
            
        except Exception as e:
            # У разі помилки Redis логуємо та пропускаємо запит
            print(f"Redis error in check_limit: {e}")
            return True

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обробник кожного вхідного запиту
        
        Args:
            handler: Наступний обробник у ланцюжку
            event: Вхідна подія (повідомлення або колбек)
            data: Додаткові дані події
            
        Returns:
            Any: Результат обробки запиту або None, якщо ліміт перевищено
        """
        # Отримуємо ID користувача з події
        user_id = event.from_user.id
        
        # Формуємо загальний ключ для всіх типів запитів користувача
        key = f"rate_limit:user:{user_id}"
        
        # Перевіряємо, чи не перевищено ліміт запитів
        is_allowed = await self.check_limit(key)
        
        if not is_allowed:
            # Якщо ліміт перевищено, надсилаємо повідомлення користувачеві
            if isinstance(event, Message):
                # Для звичайних повідомлень надсилаємо відповідь у чат
                await event.answer(
                    "Too many requests, please wait 1 seconds ⛔️",
                    parse_mode=None  # Вимикаємо парсинг HTML/Markdown
                )
            else:
                # Для колбеків показуємо спливаюче повідомлення
                await event.answer(
                    "Too many requests, please wait 1 seconds ⛔️"
                )
            return  # Перериваємо обробку запиту
        
        # Якщо ліміт не перевищено, передаємо керування наступному обробнику
        return await handler(event, data) 