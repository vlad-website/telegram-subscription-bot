import asyncio

from aiohttp import web

from bot.bot import bot, dp
from handlers.start import router as start_router
from handlers.tariffs import router as tariffs_router

from database.database import create_tables
from services.stripe_webhook import stripe_webhook

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.subscription_checker import check_subscriptions

from handlers.admin import router as admin_router


async def main():

    await create_tables()

    dp.include_router(start_router)
    dp.include_router(tariffs_router)
    dp.include_router(admin_router)

    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        check_subscriptions,
        "interval",
        hours=24
    )

    scheduler.start()

    app = web.Application()
    app.router.add_post("/stripe-webhook", stripe_webhook)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())