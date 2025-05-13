from bot.handlers.start import router as start_router
from bot.handlers.portfolio import get_portfolio_router
from bot.handlers.add_token import add_coin_router
from bot.handlers.delete_token import delete_coin_router
from bot.handlers.edit_token import edit_token_router
from bot.handlers.get_old_price import get_old_price_router
from bot.handlers.get_current_price import get_current_price_router
from bot.handlers.callbacks import router as callback_router

# Флаг для проверки, были ли уже зарегистрированы обработчики
_handlers_registered = False

def register_handlers(dp):
    """
    Регистрирует все обработчики бота в диспетчере.
    """
    global _handlers_registered

    # Защита от повторной регистрации
    if _handlers_registered:
        print("Handlers already registered, skipping.")
        return

    # Регистрируем роутеры
    try:
        dp.include_router(add_coin_router)
        dp.include_router(delete_coin_router)
        dp.include_router(edit_token_router)
        dp.include_router(get_old_price_router)
        dp.include_router(get_current_price_router)
        dp.include_router(get_portfolio_router)
        dp.include_router(callback_router)
        dp.include_router(start_router)

        # Отмечаем, что обработчики были зарегистрированы
        _handlers_registered = True
        print("All handlers successfully registered.")

    except RuntimeError as e:
        print(f"Error registering handlers: {e}")
        # Если возникает ошибка, все равно отмечаем как зарегистрированные
        _handlers_registered = True
