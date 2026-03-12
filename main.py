import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from utils.config import Config
from handlers.start import router as start_router
from handlers.tariffs import router as tariffs_router
from handlers.admin import router as admin_router
from database.database import create_tables
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.subscription_checker import check_subscriptions
from services.stripe_webhook import stripe_webhook

logging.basicConfig(level=logging.INFO)

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()
dp.include_router(start_router)
dp.include_router(tariffs_router)
dp.include_router(admin_router)

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://telegram-subscription-bot-y3mh.onrender.com/webhook"


async def on_app_startup(app: web.Application):
    await create_tables()

    # APScheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_subscriptions, "interval", hours=6, coalesce=True, max_instances=1)
    scheduler.start()

    await bot.set_webhook(WEBHOOK_URL)
    print("Bot started with webhook")


async def main():
    app = web.Application()

    # Telegram webhook
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    # Stripe webhook
    app.router.add_post("/stripe-webhook", stripe_webhook)

    # Startup
    app.on_startup.append(on_app_startup)

    return app


if __name__ == "__main__":
    import asyncio
    app = asyncio.run(main())
    web.run_app(app, host="0.0.0.0", port=10000)