import stripe
from aiohttp import web

from utils.config import Config
from services.subscription_service import grant_access

stripe.api_key = Config.STRIPE_SECRET_KEY


async def stripe_webhook(request: web.Request):

    payload = await request.text()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=Config.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return web.Response(status=400, text="Invalid signature")
    except Exception:
        return web.Response(status=400, text="Webhook error")

    # Событие оплаты завершено
    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        # Берем metadata, которую передали при создании checkout
        user_id = int(session["metadata"]["telegram_user_id"])
        plan = session["metadata"]["plan"]

        await grant_access(user_id, plan)

    return web.Response(text="ok")