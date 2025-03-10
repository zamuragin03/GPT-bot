from Config import scheduler, dp, bot
from aiogram import Dispatcher
from random import randint
from Keyboards import Keyboard
from Service import TelegramUserSubscriptionService, LocalizationService


class Tasks:
    def __init__(self):
        scheduler.add_job(Tasks.CheckSubscription,
                          'interval', seconds=120, args=(dp,))

    async def CheckSubscription(dp: Dispatcher):
        debtSubscriptions = TelegramUserSubscriptionService.CheckSubscription()
        for subscription in debtSubscriptions:
            try:
                language = subscription.get('user').get('language')
                subsctiprion_name = LocalizationService.BotTexts.GetsubscriptionName(
                    subscription.get('sub_type').get('name'), language)
                await bot.send_message(
                    subscription.get('user').get('external_id'),
                    text=LocalizationService.BotTexts.SubscriptionIsOver(language).format(
                        subsctiprion_name=subsctiprion_name
                    ),
                    reply_markup=Keyboard.Get_Subscription_Keyboard(language),
                    parse_mode='HTML'
                )
            except Exception as e:
                raise e
