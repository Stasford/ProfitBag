import logging
from aiogram import Router, types
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from bot.utils.db_pool import db
from data.models import User, UserCoin
from aiogram.filters import Command

logger = logging.getLogger(__name__)
delete_coin_router = Router()


@delete_coin_router.message(Command("delete"))
async def delete_coin(message: types.Message):
    """
    Обработчик команды /delete ТИКЕР КОЛИЧЕСТВО.
    Удаляет указанное количество криптовалюты из портфеля пользователя.
    """
    parts = message.text.split()

    if len(parts) == 2:
        # Формат /delete ТИКЕР - удаляем всю монету
        _, ticker = parts
        amount_to_delete = None
    elif len(parts) == 3:
        # Формат /delete ТИКЕР КОЛИЧЕСТВО - удаляем указанное количество
        _, ticker, amount_str = parts
        try:
            amount_to_delete = float(amount_str)
            if amount_to_delete <= 0:
                await message.reply("Количество для удаления должно быть положительным числом.")
                return
        except ValueError:
            await message.reply("Неверный формат количества. Используйте число.")
            return
    else:
        await message.reply("Неверный формат команды. Используйте: /delete ТИКЕР [КОЛИЧЕСТВО]")
        return

    ticker = ticker.upper()
    telegram_id = int(message.from_user.id)

    # Проверяем соединение с БД
    session_factory = db.get_session()
    if session_factory is None:
        logger.error("Database session factory is None in delete_coin handler")
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

            if amount_to_delete is None:
                # Удаляем монету полностью
                await session.delete(user_coin)
                await session.commit()
                await message.reply(f"Монета {ticker} полностью удалена из вашего портфеля.")
            else:
                # Проверяем, хватает ли монет
                if float(user_coin.amount) < amount_to_delete:
                    await message.reply(
                        f"У вас только {user_coin.amount} {ticker}, что меньше запрошенных {amount_to_delete}.")
                    return

                # Уменьшаем количество монет
                user_coin.amount = float(user_coin.amount) - amount_to_delete

                # Если монет не осталось, удаляем запись
                if float(user_coin.amount) <= 0:
                    await session.delete(user_coin)

                await session.commit()
                await message.reply(f"Удалено {amount_to_delete} {ticker} из вашего портфеля.")

            # Обновляем историю портфеля
            from bot.handlers.add_token import update_portfolio_history
            await update_portfolio_history(session, user.user_id)

        except SQLAlchemyError as e:
            await session.rollback()
            await message.reply("Произошла ошибка при удалении данных из базы.")
            logger.error(f"Ошибка базы данных: {e}")
