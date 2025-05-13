import logging
from aiogram import Router, types
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from bot.utils.db_pool import db
from data.models import User, UserCoin
from aiogram.filters import Command
from bot.handlers.add_token import update_portfolio_history

logger = logging.getLogger(__name__)
edit_token_router = Router()


@edit_token_router.message(Command("edit"))
async def edit_coin(message: types.Message):
    """
    Обработчик команды /edit ТИКЕР КОЛИЧЕСТВО ЦЕНА_ПОКУПКИ.
    Редактирует криптовалюту в портфеле пользователя.
    """
    # Разделение введённой команды на части
    try:
        _, ticker, new_amount, new_purchase_price = message.text.split()
        new_amount = float(new_amount)
        new_purchase_price = float(new_purchase_price)

        if new_amount <= 0:
            await message.reply("Количество монет должно быть положительным числом.")
            return

        if new_purchase_price <= 0:
            await message.reply("Цена монеты должна быть положительным числом.")
            return

    except ValueError:
        await message.reply(
            "Неверный формат команды. Используйте: /edit ТИКЕР КОЛИЧЕСТВО ЦЕНА_ПОКУПКИ")
        return

    telegram_id = int(message.from_user.id)
    ticker = ticker.upper()

    # Проверяем соединение с БД
    session_factory = db.get_session()
    if session_factory is None:
        logger.error("Database session factory is None in edit_coin handler")
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
            user_coin_result = await session.execute(select(UserCoin).filter_by(user_id=user.user_id, coin=ticker))
            user_coin = user_coin_result.scalars().first()

            if not user_coin:
                await message.reply(f"Монета {ticker} не найдена в вашем портфеле.")
                return

            # Обновление данных о монете в портфеле
            user_coin.amount = new_amount
            user_coin.purchase_price = new_purchase_price
            await session.commit()

            # Обновляем историю портфеля
            await update_portfolio_history(session, user.user_id)

            await message.reply(
                f"Монета {ticker} успешно обновлена: {new_amount} по цене {new_purchase_price}.")

        except SQLAlchemyError as e:
            await session.rollback()
            await message.reply("Произошла ошибка при обновлении данных в базе.")
            logger.error(f"Ошибка базы данных: {e}")
