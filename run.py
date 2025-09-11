import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scheduler import schedulerResetHabits, schedulerIncompletedHabits, schedulerTodayActivity
from app.core.middlewares import LanguageMiddleware, RateLimitMiddleware, SubscriptionMiddleware
from database.models import async_main
from app.handlers import __all__ as all_routers


async def main():
    redis = Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
    storage = RedisStorage(redis)

    await async_main()
    bot = Bot(
        token=os.getenv("TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        request_timeout = 60
    )

    dp = Dispatcher(storage=storage)

    # Подключаем middleware
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    dp.message.middleware(RateLimitMiddleware(redis))
    dp.callback_query.middleware(RateLimitMiddleware(redis))
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # Підключаємо всі роутери
    dp.include_routers(*all_routers)

    scheduler = AsyncIOScheduler()
    schedulerIncompletedHabits(scheduler, bot)
    schedulerTodayActivity(scheduler, bot)
    schedulerResetHabits(scheduler)
    scheduler.start()  # Запускаем планировщик

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
)
