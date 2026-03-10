from datetime import datetime
from sqlalchemy import select

from database.database import async_session
from database.models import Subscription, User
from bot.bot import bot
from utils.config import Config

from services.subscription_service import remove_user_access


async def check_subscriptions():

    async with async_session() as session:

        result = await session.execute(
            select(Subscription).where(Subscription.is_active == True)
        )

        subscriptions = result.scalars().all()

        now = datetime.utcnow()

        for sub in subscriptions:

            minutes_left = int((sub.end_date - now).total_seconds() / 60)

            user_result = await session.execute(
                select(User).where(User.id == sub.user_id)
            )

            user = user_result.scalar_one()

            telegram_id = user.telegram_id

            # уведомление за 3 дня
            if minutes_left <= 3 and not sub.notified_3_days:

                await bot.send_message(
                    telegram_id,
                    "Ваша подписка закончится через 3 дня ⚠️\n\n"
                    "Вы будете автоматически удалены из канала и чата\n\n"
                    "Продлите подписку чтобы продолжать пользоваться доступом."
                )

                sub.notified_3_days = True
                await session.commit()

            # уведомление за 1 день
            if minutes_left <= 1 and not sub.notified_1_day:

                await bot.send_message(
                    telegram_id,
                    "Ваша подписка закончится завтра ⚠️\n\n"
                    "Вы будете автоматически удалены из канала и чата\n\n"
                    "Продлите подписку чтобы продолжать пользоваться доступом."
                )

                sub.notified_1_day = True
                await session.commit()

            # если подписка закончилась
            if sub.end_date <= now:

                await remove_user_access(telegram_id)

                sub.is_active = False
                await session.commit()