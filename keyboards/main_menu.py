from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard():

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💳 Тарифы")]
        ],
        resize_keyboard=True
    )

    return keyboard