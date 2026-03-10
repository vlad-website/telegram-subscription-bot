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
                    "unit_amount": 1499 if plan == "month" else 3999,
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

    expire_date = datetime.utcnow() + timedelta(minutes=1)

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

async def activate_subscription(user_id: int, plan: str):

    async with async_session() as session:

        # ищем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )

        user = result.scalar_one_or_none()

        # если пользователя нет — создаём
        if not user:

            user = User(
                telegram_id=user_id
            )

            session.add(user)
            await session.commit()

        # определяем длительность подписки
        if plan == "month":
            minutes = 30
        else:
            minutes = 90

        start_date = datetime.utcnow()
        end_date = start_date + timedelta(minutes=minutes)

        # временно для тестов
        payment = Payment(
            user_id=user.id,
            stripe_payment_id="test_payment",
            amount=1000 if plan == "month" else 2500,
            currency="eur"
        )

        session.add(payment)
        #временно закончилось


        subscription = Subscription(
            user_id=user.id,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        session.add(subscription)
        await session.commit()

        return minutes
    
    
async def grant_access(user_id: int, plan: str):
    """
    Активирует подписку и выдаёт invite ссылки пользователю
    """
    days = await activate_subscription(user_id, plan)
    channel_link, chat_link = await create_invite_links(days)

    # вычисляем даты начала и окончания подписки
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=days)

    # форматируем даты для сообщения
    start_str = start_date.strftime("%d.%m.%Y")
    end_str = end_date.strftime("%d.%m.%Y")

    # отправляем пользователю сообщение
    await bot.send_message(
        chat_id=user_id,
        text=(
            "Оплата подтверждена ✅\n\n"
            f"Ваша подписка началась: {start_str}\n"
            f"Заканчивается: {end_str} ({days} дней)\n\n"
            "Вы будете уведомлены за 3 дня до окончания подписки.\n\n"
            "Ссылки действительны 24 часа:\n\n"
            f"Ссылка на канал:\n{channel_link}\n\n"
            f"Ссылка на чат:\n{chat_link}"
        )
    )

    # Возвращаем ссылки на случай, если нужно использовать где-то ещё
    return channel_link, chat_link