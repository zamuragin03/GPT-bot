import sys
from Commands import Tasks, SubscriptionMiddleware, CaptchaMiddleWare, GPTSubscriptionMiddleware, BannedMiddleware, AdminMiddleware
import logging
from Config import scheduler, bot, dp, router, gpt_router, admin_router, gpt_free_router
from pathlib import Path
from aiogram import Dispatcher
from aiogram.types import BotCommand
import asyncio
from pathlib import Path


async def on_startup(dispatcher: Dispatcher):
    logging.basicConfig(
        filename=Path(__file__).parent.joinpath(
            'DB_volume').joinpath("debug.log"),
        filemode="w",
        level=logging.DEBUG,
        encoding='UTF-8',
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    logging.getLogger('matplotlib.font_manager').disabled = True

    dp.include_router(admin_router)
    admin_router.message.middleware(AdminMiddleware())
    admin_router.callback_query.middleware(AdminMiddleware())

    dp.include_router(router)
    # router.message.middleware(CaptchaMiddleWare())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    dp.include_router(gpt_router)
    gpt_router.message.middleware(GPTSubscriptionMiddleware())
    gpt_router.callback_query.middleware(GPTSubscriptionMiddleware())

    dp.include_router(gpt_free_router)

    dp.message.middleware(BannedMiddleware())
    dp.callback_query.middleware(BannedMiddleware())
    scheduler.start()
    Tasks()


async def on_shutdown(dispatcher: Dispatcher):
    scheduler.shutdown(wait=False)
    logging.info("Scheduler stopped.")


async def main() -> None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    if len(sys.argv)==1:
        exit('dev or build?')

    asyncio.run(main())
