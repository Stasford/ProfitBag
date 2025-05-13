import logging
from aiogram import Router, types
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from bot.utils.db_pool import db  # Заменено с AsyncSessionLocal
from data.models import User, UserCoin
from aiogram.filters import Command

logger = logging.getLogger(__name__)
get_old_price_router = Router()

@get_old_price_router.message(Command("get_price"))
async def get_old_price(message: types.Message):
    """
    Обработчик команды /get_price <тикер>.
    Отображает цену покупки указанной монеты в портфеле пользователя.
    """
    # Разделение введённой команды на части
    try:
        _, ticker = message.text.split()
    except ValueError:
        await message.reply("Неверный формат команды. Используйте: /get_price [тикер]")
        return

    telegram_id = int(message.from_user.id)  # Изменено со str на int

    # Проверяем соединение с БД
    session_factory = db.get_session()
    if session_factory is None:
        logger.error("Database session factory is None in get_old_price handler")
        await message.reply("Ошибка: соединение с базой данных не установлено.")
        return

    async with session_factory() as session:
        try:
            # Проверка наличия пользователя в базе
            result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
            user = result.scalars().first()

            if not user:
                await message.reply("Пользователь не найден в базе данных.")
                return

            # Поиск монеты в портфеле пользователя
            user_coin = await session.execute(
                select(UserCoin).filter_by(user_id=user.user_id, coin=ticker.upper())
            )
            user_coin = user_coin.scalars().first()

            if not user_coin:
                await message.reply(f"Монета {ticker.upper()} не найдена в вашем портфеле.")
                return

            # Отправка сообщения с ценой покупки монеты
            await message.reply(
                f"Цена покупки монеты {ticker.upper()}: {user_coin.purchase_price}"
            )

        except SQLAlchemyError as e:
            await message.reply("Произошла ошибка при получении данных из базы.")
            logger.error(f"Ошибка базы данных: {e}")
