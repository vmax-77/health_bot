import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings
from handlers import (
    start, profile, water, food, 
    workout, progress, recommendations
)
from os import getenv
from database import init_db
from middlewares.logging_middleware import LoggingMiddleware

# Получаем токен из переменных окружения
TOKEN = getenv("BOT_TOKEN")

if TOKEN is None:
    raise ValueError("Ошибка: Токен бота не найден! Проверьте файл .env")

async def main():
    # Настраиваем логирование с детальной информацией
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("bot_logs.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    
    # Инициализация базы данных (синхронно)
    init_db()
    logging.info("База данных инициализирована")
    
    # Инициализация бота и диспетчера
    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Добавляем middleware для логирования
    dp.update.middleware(LoggingMiddleware())
    
    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(water.router)
    dp.include_router(food.router)
    dp.include_router(workout.router)
    dp.include_router(progress.router)
    dp.include_router(recommendations.router)
    
    logging.info("Бот запускается...")
    
    # Запуск бота с очисткой обновлений
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")