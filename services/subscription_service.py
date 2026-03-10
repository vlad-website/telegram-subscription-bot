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

async def create_invite_links(days: int):

    expire_date = datetime.utcnow() + timedelta(days=1)

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
            days = 30
        else:
            days = 90

        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days)

        # временно для тестов
        payment = Payment(
            user_id=user.id,
            stripe_payment_id="test_payment",
            amount=1000 if plan == "month" else 2500,
            currency="eur"
        )

        session.add(payment)



        subscription = Subscription(
            user_id=user.id,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        session.add(subscription)
        await session.commit()

        return days
    
    
async def grant_access(user_id: int, plan: str):

    days = await activate_subscription(user_id, plan)

    channel_link, chat_link = await create_invite_links(days)

    return channel_link, chat_link