import stripe
from aiohttp import web

from utils.config import Config

stripe.api_key = Config.STRIPE_SECRET_KEY


async def stripe_webhook(request):

    payload = await request.text()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            Config.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return web.Response(status=400, text=str(e))

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        telegram_user_id = session["metadata"]["telegram_user_id"]
        plan = session["metadata"]["plan"]

        print("Payment success:", telegram_user_id, plan)

        # здесь позже будет:
        # создание подписки
        # выдача invite ссылки

    return web.Response(text="ok")