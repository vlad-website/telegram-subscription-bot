from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def tariffs_keyboard():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="1 месяц 14.99€",
                    callback_data="buy_month"
                )
            ],
            [
                InlineKeyboardButton(
                    text="3 месяца 39.99€",
                    callback_data="buy_3months"
                )
            ]
        ]
    )
    return keyboard

def renew_subscription_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Продлить подписку",
                    callback_data="tariffs"
                )
            ]
        ]
    )

    return keyboard