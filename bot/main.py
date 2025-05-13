import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, DATABASE_URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from bot.handlers import register_handlers
from bot.utils.api_requests import test_fetch_binance_price
from bot.utils.db_pool import db
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from data.models import Base

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    """Создает таблицы в базе данных, если они не существуют."""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    logging.info("Database tables created successfully")

async def setup_bot_commands(bot):
    commands = [
        BotCommand(command='start', description='Начать работу с ботом'),
        BotCommand(command='add', description='Добавить криптовалюту (формат: ТИКЕР КОЛИЧЕСТВО ЦЕНА)'),
        BotCommand(command='portfolio', description='Показать мой портфель'),
        BotCommand(command='get_price', description='Узнать текущую цену криптовалюты'),
        BotCommand(command='edit', description='Редактировать данные о криптовалюте'),
        BotCommand(command='delete', description='Удалить криптовалюту из портфеля')
    ]
    await bot.set_my_commands(commands)


async def main():
    # Создание асинхронного движка для подключения к базе данных
    engine = create_async_engine(DATABASE_URL, echo=True)

    # Создание фабрики асинхронных сессий
    session_factory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Инициализация соединения с базой данных
    db.initialize(session_factory)

    # Инициализация хранилища состояний
    storage = MemoryStorage()

    # Инициализация бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Создание диспетчера
    dp = Dispatcher(storage=storage)

    # Регистрация обработчиков
    register_handlers(dp)

    # Установка команд бота
    await setup_bot_commands(bot)

    # Создание таблиц в базе данных
    await create_tables()

    # Запуск поллинга
    try:
        logger.info("Бот запущен. Начало поллинга...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await engine.dispose()


if __name__ == '__main__':
    # Запускаем тест API запроса только один раз
    asyncio.run(test_fetch_binance_price())
    # Затем запускаем основную функцию
    asyncio.run(main())
