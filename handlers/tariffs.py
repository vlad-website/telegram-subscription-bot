from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards.tariffs import tariffs_keyboard
from services.subscription_service import create_checkout_session

from services.subscription_service import create_invite_links

from services.subscription_service import grant_access

router = Router()


@router.message(lambda message: message.text == "💳 Тарифы")
async def show_tariffs(message: Message):

    text = (
        """Ты не просто оформляешь подписку 💫  
Ты входишь в закрытый женский круг,  
где тебя понимают с полуслова. 🤍

Каждый месяц в клубе тебя ждут:

🏋️‍♀️ тренировки, рецепты и полезные лайфхаки  
🎧 подкасты, советы, мои фишечки и секреты  
💬 закрытый чат для общения и поддержки  
🧘‍♀️ практики, ритуалы и закрытые материалы  
✨ пространство, где можно быть собой

Это больше, чем клуб.  
Это место силы для женщин. 🌙"""
    )

    await message.answer(
        text,
        reply_markup=tariffs_keyboard()
    )


@router.message(Command("test_invite"))
async def test_invite(message: Message):

    channel_link, chat_link = await create_invite_links(30)

    await message.answer(
        f"Channel:\n{channel_link}\n\nChat:\n{chat_link}"
    )

@router.message(Command("activate_test"))
async def activate_test(message: Message):

    channel_link, chat_link = await grant_access(
        message.from_user.id,
        "month"
    ) 

    await message.answer(
        "Оплата подтверждена ✅\n\n"
        "Ссылки действительны 24 часа\n\n"
        f"Ссылка на канал:\n{channel_link}\n\n"
        f"Ссылка на чат:\n{chat_link}"
    )

@router.callback_query(lambda c: c.data == "buy_month")
async def buy_month(callback: CallbackQuery):

    url = await create_checkout_session(
        user_id=callback.from_user.id,
        plan="month"
    )

    await callback.message.answer(
        f"Оплатите подписку:\n{url}"
    )


@router.callback_query(lambda c: c.data == "buy_3months")
async def buy_three_months(callback: CallbackQuery):

    url = await create_checkout_session(
        user_id=callback.from_user.id,
        plan="three_months"
    )

    await callback.message.answer(
        f"Оплатите подписку:\n{url}"
    )