from Config import scheduler, dp, bot
from aiogram import Dispatcher
from random import randint
from Keyboards import Keyboard
from Service import TelegramUserSubscriptionService


class Tasks:
    async def check_messages(dp: Dispatcher):
        ...

    async def CheckSubscription(dp: Dispatcher):
        debtUsers = TelegramUserSubscriptionService.CheckTrialSubscription()
        for user in debtUsers:
            try:
                await bot.send_message(
                    user.get('external_id'),
                    text=f'У вас закончилась пробная подписка. Может продлим?',
                    reply_markup=Keyboard.Get_Subscription_Keyboard('ru'),
                    parse_mode='HTML'
                )
            except Exception as e:
                raise e
