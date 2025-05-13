import logging
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from data.models import User, UserCoin
from bot.utils.db_pool import db

logger = logging.getLogger(__name__)
add_coin_router = Router()


@add_coin_router.message(Command("add"))
async def add_coin(message: types.Message):
    """
    Обработчик команды /add ТИКЕР КОЛИЧЕСТВО ЦЕНА_ПОКУПКИ.
    Добавляет криптовалюту в портфель пользователя.
    """
    parts = message.text.split()

    if len(parts) != 4:
        await message.reply("Неверный формат команды. Используйте: /add ТИКЕР КОЛИЧЕСТВО ЦЕНА_ПОКУПКИ")
        return

    _, ticker, amount_str, price_str = parts

    try:
        amount = float(amount_str)
        purchase_price = float(price_str)
    except ValueError:
        await message.reply(
            "Ошибка! Количество и цена должны быть числами. Используйте: /add ТИКЕР КОЛИЧЕСТВО ЦЕНА_ПОКУПКИ")
        return

    telegram_id = int(message.from_user.id)

    # Проверяем соединение с БД
    session_factory = db.get_session()
    if session_factory is None:
        logger.error("Database session factory is None in add_coin handler")
        await message.reply("Ошибка: соединение с базой данных не установлено.")
        return

    # Теперь пробуем выполнить операции с базой данных
    try:
        async with session_factory() as session:
            try:
                # Проверка наличия пользователя в базе
                result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
                user = result.scalars().first()

                if not user:
                    # Создание нового пользователя, если его нет в базе
                    user = User(telegram_id=telegram_id)
                    session.add(user)
                    await session.commit()

                # Проверяем, есть ли монета в портфеле
                coin_result = await session.execute(
                    select(UserCoin).filter_by(user_id=user.user_id, coin=ticker.upper())
                )
                user_coin = coin_result.scalars().first()

                if user_coin:
                    # Если монета есть, обновляем количество и среднюю цену
                    old_total = float(user_coin.amount) * float(user_coin.purchase_price)
                    new_total = amount * purchase_price
                    new_amount = float(user_coin.amount) + amount

                    # Рассчитываем средневзвешенную цену
                    user_coin.purchase_price = (old_total + new_total) / new_amount
                    user_coin.amount = new_amount
                else:
                    # Если монеты нет, добавляем новую запись
                    user_coin = UserCoin(user_id=user.user_id, coin=ticker.upper(), amount=amount,
                                         purchase_price=purchase_price)
                    session.add(user_coin)

                await session.commit()

                # Обновляем историю портфеля
                await update_portfolio_history(session, user.user_id)

                await message.reply(f"Добавлено {amount} {ticker.upper()} в ваш портфель.")

            except SQLAlchemyError as e:
                await session.rollback()
                await message.reply("Произошла ошибка при добавлении данных в базу.")
                logger.error(f"Ошибка базы данных: {e}")
    except Exception as e:
        logger.error(f"Error in database operation: {e}")
        await message.reply("Произошла ошибка при работе с базой данных.")


async def update_portfolio_history(session, user_id):
    """Обновляет историю стоимости портфеля"""
    from data.models import PortfolioHistory

    try:
        # Вычисляем текущую стоимость портфеля
        result = await session.execute(select(UserCoin).filter_by(user_id=user_id))
        coins = result.scalars().all()

        total_value = sum(float(coin.amount) * float(coin.purchase_price) for coin in coins)

        # Записываем в историю
        history_record = PortfolioHistory(user_id=user_id, total_value=total_value)
        session.add(history_record)
        await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при обновлении истории портфеля: {e}")
