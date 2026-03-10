from datetime import datetime

from sqlalchemy import select

from database.database import async_session
from database.models import Subscription, User
from bot.bot import bot
from utils.config import Config

async def check_subscriptions():

    async with async_session() as session:

        result = await session.execute(
            select(Subscription).where(Subscription.is_active == True)
        )

        subscriptions = result.scalars().all()

        now = datetime.utcnow()

        for sub in subscriptions:

            days_left = (sub.end_date - now).days

            user_result = await session.execute(
                select(User).where(User.id == sub.user_id)
            )

            user = user_result.scalar_one()

            telegram_id = user.telegram_id

            # уведомление за 3 дня
            if days_left == 3:

                await bot.send_message(
                    telegram_id,
                    "Ваша подписка закончится через 3 дня ⚠️\n\n"
                    "Вы будете автоматически удалены из канала и чата\n\n"
                    "Продлите подписку чтобы продолжать пользоваться чатом и группой"
                )

            # уведомление за 1 день
            if days_left == 1:

                await bot.send_message(
                    telegram_id,
                    "Ваша подписка закончится завтра ⚠️\n\n"
                    "Вы будете автоматически удалены из канала и чата\n\n"
                    "Продлите подписку чтобы продолжать пользоваться чатом и группой"
                )

            # если подписка закончилась
            if days_left < 0:

                await remove_user_access(telegram_id)

                sub.is_active = False

                await session.commit()



async def remove_user_access(telegram_id: int):

    try:

        await bot.ban_chat_member(
            chat_id=Config.CHANNEL_ID,
            user_id=telegram_id
        )

        await bot.unban_chat_member(
            chat_id=Config.CHANNEL_ID,
            user_id=telegram_id
        )

    except:
        pass

    try:

        await bot.ban_chat_member(
            chat_id=Config.CHAT_ID,
            user_id=telegram_id
        )

        await bot.unban_chat_member(
            chat_id=Config.CHAT_ID,
            user_id=telegram_id
        )

    except:
        pass

    try:

        await bot.send_message(
            telegram_id,
            "Ваша подписка закончилась. Доступ был закрыт.\n\n"
            "Продлите подписку чтобы снова получить доступ"
        )

    except:
        pass