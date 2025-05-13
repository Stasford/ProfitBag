from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.future import select
import logging
from data.models import User, UserCoin, PortfolioHistory
from bot.utils.db_pool import db
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io

get_portfolio_router = Router()
logger = logging.getLogger(__name__)


@get_portfolio_router.message(Command("portfolio"))
async def show_portfolio(message: types.Message):
    """
    Обработчик команды /portfolio.
    Отображает криптовалюты в портфеле пользователя.
    """
    # Отправляем начальное сообщение
    status_msg = await message.answer("Запрашиваю данные о вашем портфеле...")

    try:
        # Получаем ID пользователя
        telegram_id = int(message.from_user.id)
        logger.info(f"Запрос портфеля для пользователя {telegram_id}")

        # Получаем соединение с базой данных
        session_factory = db.get_session()
        if session_factory is None:
            logger.error("Database session factory is None")
            await status_msg.edit_text("⚠️ Ошибка: соединение с базой данных не установлено.")
            return

        # Открываем сессию
        async with session_factory() as session:
            # Находим пользователя в базе данных
            logger.info(f"Поиск пользователя {telegram_id} в базе данных")
            result = await session.execute(
                select(User).filter_by(telegram_id=telegram_id)
            )
            user = result.scalars().first()

            # Проверяем наличие пользователя
            if not user:
                logger.info(f"Пользователь {telegram_id} не найден в базе данных")
                await status_msg.edit_text("У вас пока нет портфеля. Используйте /add для добавления криптовалюты.")
                return

            logger.info(f"Пользователь найден, ID={user.user_id}")

            # Получаем список монет пользователя
            logger.info(f"Запрос монет для пользователя {user.user_id}")
            coins_result = await session.execute(
                select(UserCoin).filter_by(user_id=user.user_id)
            )
            user_coins = list(coins_result.scalars().all())  # Преобразуем в список немедленно

            # Проверяем наличие монет
            if not user_coins:
                logger.info(f"У пользователя {telegram_id} нет монет в портфеле")
                await status_msg.edit_text("Ваш портфель пуст. Используйте /add для добавления криптовалюты.")
                return

            # Собираем данные по монетам, группируя их по тикеру
            coin_data = {}
            total_value = 0

            for coin in user_coins:
                ticker = coin.coin
                amount = float(coin.amount)
                price = float(coin.purchase_price)
                value = amount * price
                total_value += value

                if ticker not in coin_data:
                    coin_data[ticker] = {
                        'amount': amount,
                        'price': price,
                        'value': value
                    }
                else:
                    # Это не должно происходить после внесенных изменений,
                    # но оставим для совместимости
                    coin_data[ticker]['amount'] += amount
                    coin_data[ticker]['value'] += value
                    coin_data[ticker]['price'] = coin_data[ticker]['value'] / coin_data[ticker]['amount']

            # Формируем сообщение с портфелем
            logger.info(f"Найдено {len(coin_data)} монет в портфеле")
            portfolio_text = "📊 <b>Ваш криптопортфель:</b>\n\n"

            for ticker, data in coin_data.items():
                portfolio_text += (
                    f"🪙 <b>{ticker}</b>: {data['amount']:.8f} монет\n"
                    f"   💰 Цена покупки: {data['price']:.2f} USDT\n"
                    f"   💵 Стоимость: {data['value']:.2f} USDT\n\n"
                )

            portfolio_text += f"<b>Общая стоимость портфеля:</b> {total_value:.2f} USDT"

            # Отправляем сообщение с портфелем
            await status_msg.edit_text(portfolio_text)
            logger.info(f"Портфель успешно отображен для пользователя {telegram_id}")

    except Exception as e:
        # Подробный вывод ошибки в лог
        logger.error(f"Ошибка при отображении портфеля: {e}", exc_info=True)

        # Информативное сообщение пользователю
        await status_msg.edit_text(
            f"⚠️ Произошла ошибка при получении данных портфеля.\n"
            f"Тип ошибки: {type(e).__name__}\n"
            f"Попробуйте позже или обратитесь к администратору."
        )


@get_portfolio_router.callback_query(lambda c: c.data == "portfolio_change")
async def show_portfolio_history(callback: types.CallbackQuery):
    """
    Обработчик кнопки "Динамика портфеля".
    Показывает историю изменения стоимости портфеля.
    """
    await callback.answer()
    status_msg = await callback.message.answer("Запрашиваю данные об изменении вашего портфеля...")

    try:
        telegram_id = int(callback.from_user.id)

        session_factory = db.get_session()
        if session_factory is None:
            await status_msg.edit_text("⚠️ Ошибка: соединение с базой данных не установлено.")
            return

        async with session_factory() as session:
            # Находим пользователя
            user_result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
            user = user_result.scalars().first()

            if not user:
                await status_msg.edit_text("Пользователь не найден в базе данных.")
                return

            # Получаем историю портфеля
            history_result = await session.execute(
                select(PortfolioHistory)
                .filter_by(user_id=user.user_id)
                .order_by(PortfolioHistory.timestamp.desc())
                .limit(20)
            )
            history = list(history_result.scalars().all())

            if not history:
                await status_msg.edit_text(
                    "Данные о динамике портфеля отсутствуют. Добавьте или удалите монеты для начала отслеживания."
                )
                return

            # Формируем текстовый отчет
            text = "📈 <b>Динамика стоимости портфеля:</b>\n\n"

            # Выводим последние 10 записей в обратном порядке (от старых к новым)
            for record in list(reversed(history))[:10]:
                date_str = record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                text += f"{date_str}: {float(record.total_value):.2f} USDT\n"

            # Находим изменение за последние сутки
            if len(history) >= 2:
                latest_value = float(history[0].total_value)
                oldest_value = float(history[-1].total_value)
                percent_change = ((latest_value - oldest_value) / oldest_value) * 100 if oldest_value > 0 else 0

                text += f"\n<b>Общее изменение:</b> {percent_change:.2f}%"

                if percent_change > 0:
                    text += " 📈"
                elif percent_change < 0:
                    text += " 📉"

            await status_msg.edit_text(text)

    except Exception as e:
        logger.error(f"Ошибка при отображении динамики портфеля: {e}", exc_info=True)
        await status_msg.edit_text(
            f"⚠️ Произошла ошибка при получении данных динамики портфеля.\n"
            f"Тип ошибки: {type(e).__name__}\n"
            f"Попробуйте позже или обратитесь к администратору."
        )
