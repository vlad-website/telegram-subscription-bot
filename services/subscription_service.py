import stripe

from datetime import datetime, timedelta

from bot.bot import bot

from utils.config import Config

from database.database import async_session
from database.models import User, Subscription, Payment

from sqlalchemy import select

stripe.api_key = Config.STRIPE_SECRET_KEY


async def create_checkout_session(user_id: int, plan: str):

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",

        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": f"Подписка {plan}",
                    },
                    "unit_amount": 99 if plan == "month" else 3999,
                },
                "quantity": 1,
            }
        ],

        metadata={
            "telegram_user_id": user_id,
            "plan": plan
        },

        success_url="https://t.me/RaznayaFit_Bot",
        cancel_url="https://t.me/RaznayaFit_Bot"
    )

    return session.url

async def create_invite_links(minutes: int):

    expire_date = datetime.utcnow() + timedelta(minutes=minutes)

    channel_link = await bot.create_chat_invite_link(
        chat_id=Config.CHANNEL_ID,
        expire_date=expire_date,
        member_limit=1
    )

    chat_link = await bot.create_chat_invite_link(
        chat_id=Config.CHAT_ID,
        expire_date=expire_date,
        member_limit=1
    )

    return channel_link.invite_link, chat_link.invite_link

#временная функция
async def deactivate_old_subscriptions(user_id: int):
    """Деактивирует все старые подписки пользователя."""
    async with async_session() as session:
        result = await session.execute(
            select(Subscription).where(Subscription.user_id == user_id, Subscription.is_active == True)
        )
        active_subs = result.scalars().all()

        for sub in active_subs:
            sub.is_active = False
            # Можно сбросить уведомления, если нужно:
            sub.notified_3_days = False
            sub.notified_1_day = False

        await session.commit()
        print(f"Deactivated {len(active_subs)} old subscriptions for user {user_id}")

async def activate_subscription(user_id: int, plan: str):
    async with async_session() as session:

        # 1️⃣ ищем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            user = User(telegram_id=user_id)
            session.add(user)
            await session.commit()

        # 2️⃣ определяем длительность подписки
        minutes = 5 if plan == "month" else 10
        now = datetime.utcnow()

        # 3️⃣ создаём временный платеж для теста
        payment = Payment(
            user_id=user.id,
            stripe_payment_id="test_payment",
            amount=1499 if plan == "month" else 3999,
            currency="eur"
        )
        session.add(payment)

        # 4️⃣ ищем активную подписку
        result = await session.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.is_active == True
            )
        )
        active_sub = result.scalar_one_or_none()

        if active_sub and active_sub.end_date > now:
            # 5️⃣ если подписка активна, прибавляем минуты
            active_sub.end_date += timedelta(minutes=minutes)
            active_sub.notified_3_days = False
            active_sub.notified_1_day = False
            print(f"Extended subscription for user {user_id} by {minutes} minutes, new end_date: {active_sub.end_date}")

        else:
            # 6️⃣ если подписки нет или она закончилась, создаём новую
            start_date = now
            end_date = start_date + timedelta(minutes=minutes)
            subscription = Subscription(
                user_id=user.id,
                plan=plan,
                start_date=start_date,
                end_date=end_date,
                is_active=True,
                notified_3_days=False,
                notified_1_day=False
            )
            session.add(subscription)
            print(f"Created new subscription for user {user_id}, end_date: {end_date}")

        await session.commit()
        return minutes
    
    
async def grant_access(user_id: int, plan: str):
    """
    Активирует подписку и выдаёт invite ссылки пользователю
    """
    minutes = await activate_subscription(user_id, plan)
    channel_link, chat_link = await create_invite_links(minutes)

    # вычисляем даты начала и окончания подписки
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(minutes=minutes)

    # форматируем даты для сообщения
    start_str = start_date.strftime("%d.%m.%Y")
    end_str = end_date.strftime("%d.%m.%Y")

    # отправляем пользователю сообщение
    await bot.send_message(
        chat_id=user_id,
        text=(
            "Оплата подтверждена ✅\n\n"
            f"Ваша подписка началась: {start_str}\n"
            #f"Заканчивается: {end_str} ({days} дней)\n\n"
            "Вы будете уведомлены за 3 дня до окончания подписки.\n\n"
            "Ссылки действительны 24 часа:\n\n"
            f"Ссылка на канал:\n{channel_link}\n\n"
            f"Ссылка на чат:\n{chat_link}"
        )
    )

    # Возвращаем ссылки на случай, если нужно использовать где-то ещё
    return channel_link, chat_link

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