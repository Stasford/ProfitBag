from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    """Создает инлайн-клавиатуру для основного меню"""
    buttons = [
        [
            InlineKeyboardButton(text="💰 Узнать цену", callback_data="cmd_price"),
            InlineKeyboardButton(text="📊 Мой портфель", callback_data="cmd_portfolio")
        ],
        [
            InlineKeyboardButton(text="➕ Добавить монету", callback_data="cmd_add"),
            InlineKeyboardButton(text="➖ Удалить монету", callback_data="cmd_remove")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_command_buttons():
    """Создает клавиатуру с кнопками команд"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/price"), KeyboardButton(text="/add")],
            [KeyboardButton(text="/remove"), KeyboardButton(text="/portfolio")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return keyboard
