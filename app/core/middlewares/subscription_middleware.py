from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import app.keyboards as kb
from app.core.utils.config import CHANNEL



class SubscriptionMiddleware(BaseMiddleware):
    """Middleware для перевірки підписки користувача на канал"""
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Перевіряє підписку користувача на канал
        
        Args:
            handler: Наступний обробник
            event: Вхідна подія
            data: Додаткові дані
        """
        # Пропускаємо команду /start та перевірку підписки
        if isinstance(event, Message) and event.text and event.text.startswith("/info"):
            return await handler(event, data)
        if isinstance(event, CallbackQuery) and event.data == "check_subscription":
            return await handler(event, data)

        user_id = event.from_user.id
        bot = event.bot

        try:
            member = await bot.get_chat_member(chat_id=CHANNEL, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                raise ValueError("User is not a channel member")
        except Exception as e:
            print(f"Error in subscription middleware: {e}")
            # Якщо перевірка не вдалася, показуємо повідомлення про підписку
            if isinstance(event, Message):
                await event.answer(
                    "Для роботи бота необхідно підписатися на наш канал. Будь ласка, підпишіться, щоб продовжити. 👍",
                    reply_markup=await kb.subscriptionKeyboard()
                )
            elif isinstance(event, CallbackQuery):
                # Для колбека check_subscription показуємо спливаюче вікно
                if event.data == "check_subscription":
                    await event.answer(
                        "Ви все ще не підписані. Будь ласка, підпишіться.",
                        show_alert=True
                    )
                else:
                    # Для інших колбеків надсилаємо нове повідомлення
                    await event.message.answer(
                        "Для роботи бота необхідно підписатися на наш канал. Будь ласка, підпишіться, щоб продовжити. 👍",
                        reply_markup=await kb.subscriptionKeyboard()
                    )
                    await event.answer() # Закриваємо старий колбек
            return # Зупиняємо подальшу обробку

        # Якщо перевірка успішна, передаємо керування наступному обробнику
        return await handler(event, data) 