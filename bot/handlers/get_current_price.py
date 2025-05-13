import logging
from aiogram import Router, types
from bot.utils.api_requests import fetch_binance_price
from aiogram.filters import Command


logger = logging.getLogger(__name__)
get_current_price_router = Router()


@get_current_price_router.message(Command("get_price"))
async def get_current_price(message: types.Message):
    """
    Обработчик команды /get_price <тикер>.
    Отображает текущую рыночную цену указанной монеты.
    """
    # Разделение введённой команды на части
    try:
        _, ticker = message.text.split()
    except ValueError:
        await message.reply("Неверный формат команды. Используйте: /get_price <тикер>")
        return

    ticker = ticker.upper()
    try:
        # Получение текущей цены монеты с помощью функции fetch_binance_price
        price = await fetch_binance_price(ticker)
        await message.reply(f"Текущая цена {ticker}: {price} USDT")
    except ValueError as e:
        await message.reply(str(e))
        logger.error(f"Ошибка при получении цены для {ticker}: {e}")
