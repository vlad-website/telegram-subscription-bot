import stripe
import traceback
from aiohttp import web

from utils.config import Config
from services.subscription_service import grant_access

stripe.api_key = Config.STRIPE_SECRET_KEY


async def stripe_webhook(request: web.Request):

    print("🔥 WEBHOOK CALLED")

    payload = await request.text()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            Config.STRIPE_WEBHOOK_SECRET
        )
        print("✅ Signature verified")

    except Exception as e:
        print("❌ SIGNATURE ERROR")
        print(e)
        return web.Response(status=400, text="Signature error")

    try:

        print("📩 Event type:", event["type"])

        if event["type"] == "checkout.session.completed":

            session = event["data"]["object"]

            print("SESSION DATA:", session)

            metadata = session.get("metadata", {})

            print("METADATA:", metadata)

            user_id = int(metadata["telegram_user_id"])
            plan = metadata["plan"]

            print("USER:", user_id)
            print("PLAN:", plan)

            await grant_access(user_id, plan)

            print("✅ ACCESS GRANTED")

    except Exception as e:

        print("❌ PROCESSING ERROR")
        traceback.print_exc()

        return web.Response(status=400, text="Processing error")

    return web.Response(text="ok")