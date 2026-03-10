from datetime import datetime
from sqlalchemy import select

from database.database import async_session
from database.models import Subscription, User
from bot.bot import bot
from services.subscription_service import remove_user_access

import logging
logging.basicConfig(level=logging.INFO)


async def check_subscriptions():
    logging.info("check_subscriptions called")

    async with async_session() as session:
        # Берём все активные подписки
        result = await session.execute(
            select(Subscription).where(Subscription.is_active == True)
        )
        subscriptions = result.scalars().all()
        now = datetime.utcnow()

        for sub in subscriptions:
            minutes_left = (sub.end_date - now).total_seconds() / 60

            # Получаем пользователя
            user_result = await session.execute(
                select(User).where(User.id == sub.user_id)
            )
            user = user_result.scalar_one()
            telegram_id = user.telegram_id

            logging.info(f"Subscription for user {telegram_id}: {minutes_left:.2f} minutes left")

            # --- Уведомление за 3 минуты ---
            if minutes_left <= 3 and not sub.notified_3_days and minutes_left > 0:
                try:
                    await bot.send_message(
                        telegram_id,
                        "⚠️ Ваша подписка закончится через 3 минуты!\n\n"
                        "Вы будете автоматически удалены из канала и чата, "
                        "если не продлите подписку."
                    )
                    logging.info(f"Sent 3-min warning to {telegram_id}")
                except Exception as e:
                    logging.error(f"Failed to send 3-min warning to {telegram_id}: {e}")

                sub.notified_3_days = True
                await session.commit()

            # --- Уведомление за 1 минуту ---
            if minutes_left <= 1 and not sub.notified_1_day and minutes_left > 0:
                try:
                    await bot.send_message(
                        telegram_id,
                        "⚠️ Ваша подписка закончится через 1 минуту!\n\n"
                        "Вы будете автоматически удалены из канала и чата, "
                        "если не продлите подписку."
                    )
                    logging.info(f"Sent 1-min warning to {telegram_id}")
                except Exception as e:
                    logging.error(f"Failed to send 1-min warning to {telegram_id}: {e}")

                sub.notified_1_day = True
                await session.commit()

            # --- Если подписка закончилась ---
            if sub.end_date <= now:
                try:
                    await remove_user_access(telegram_id)
                    logging.info(f"Removed access for user {telegram_id}")
                except Exception as e:
                    logging.error(f"Failed to remove access for {telegram_id}: {e}")

                sub.is_active = False
                await session.commit()
                logging.info(f"Subscription for user {telegram_id} deactivated")