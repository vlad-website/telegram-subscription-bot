from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from sqlalchemy import select, func

from database.database import async_session
from database.models import User, Payment, Subscription

from utils.config import Config

router = Router()

def is_admin(user_id: int):

    return user_id == Config.ADMIN_ID

@router.message(Command("admin"))
async def admin_panel(message: Message):

    if not is_admin(message.from_user.id):
        return

    async with async_session() as session:

        users_count = await session.scalar(
            select(func.count()).select_from(User)
        )

        payments_count = await session.scalar(
            select(func.count()).select_from(Payment)
        )

        active_subscriptions = await session.scalar(
            select(func.count()).select_from(Subscription).where(
                Subscription.is_active == True
            )
        )

    text = (
        "📊 Статистика бота\n\n"
        f"👥 Пользователей: {users_count}\n"
        f"💳 Оплат: {payments_count}\n"
        f"🔥 Активных подписок: {active_subscriptions}"
    )

    await message.answer(text)