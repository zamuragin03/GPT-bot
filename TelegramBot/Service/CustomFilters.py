from aiogram.filters import Filter
from aiogram import types
from Service import TelegramUserSubscriptionService


class SubscriberUser(Filter):
    def __init__(self,) -> None:
        ...

    async def __call__(self, message: types.Message) -> bool:
        from Keyboards import Keyboard
        if TelegramUserSubscriptionService.GetUserActiveSubscription(message.from_user.id):
            return True
        else:
            await message.answer(
                text='У вас не актииврована подписка. Для пользования ботом, приобретите ее',
                reply_markup=Keyboard.Get_Subscription_Keyboard('ru')
            )
            return False
