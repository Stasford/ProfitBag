from aiogram import Router, types, F
from bot.utils.keyboards import get_main_menu
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "cmd_price")
async def price_callback(callback: types.CallbackQuery):
    try:
        await callback.answer()
        await callback.message.answer(
            "Для получения цены криптовалюты используйте формат:\n/price ТИКЕР\n\nНапример: /price BTC")
    except Exception as e:
        logger.error(f"Ошибка в price_callback: {e}")


@router.callback_query(F.data == "cmd_add")
async def add_callback(callback: types.CallbackQuery):
    try:
        await callback.answer()
        await callback.message.answer(
            "Для добавления криптовалюты используйте формат:\n/add ТИКЕР КОЛИЧЕСТВО ЦЕНА\n\nНапример: /add BTC 0.1 45000")
    except Exception as e:
        logger.error(f"Ошибка в add_callback: {e}")


@router.callback_query(F.data == "cmd_remove")
async def remove_callback(callback: types.CallbackQuery):
    try:
        await callback.answer()
        await callback.message.answer(
            "Для удаления криптовалюты из портфеля используйте формат:\n/remove ТИКЕР [КОЛИЧЕСТВО]\n\nНапример: /remove BTC или /remove BTC 0.05")
    except Exception as e:
        logger.error(f"Ошибка в remove_callback: {e}")


@router.callback_query(F.data == "cmd_portfolio")
async def portfolio_callback(callback: types.CallbackQuery):
    try:
        await callback.answer()
        # Показываем сообщение о выполнении
        await callback.message.answer("Запрашиваю данные о вашем портфеле...")

        # Вызываем функцию отображения портфеля
        from bot.handlers.portfolio import show_portfolio
        await show_portfolio(callback.message)
    except Exception as e:
        logger.error(f"Ошибка в portfolio_callback: {e}", exc_info=True)
        await callback.message.answer(f"Произошла ошибка при получении портфеля: {str(e)[:100]}...")
