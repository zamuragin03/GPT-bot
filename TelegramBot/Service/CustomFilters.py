from aiogram.filters import Filter
from aiogram import types
from Service import TelegramUserSubscriptionService, LocalizationService
from Config import SUBSCRIPTION_LIMITATIONS,DAILY_LIMITATIONS
from aiogram import types
from typing import Union



class DocumentTypeFilter(Filter):
    def __init__(self, document_types):
        self.document_types = document_types

    async def __call__(self, message: types.Message) -> bool:
        if message.document:
            file_extension = message.document.file_name.split('.')[-1].lower()
            return file_extension in self.document_types
        return False


class gptTypeFilter(Filter):
    def __init__(self, action_type):
        self.action_type = action_type

    async def __call__(self, event: Union[types.Message, types.CallbackQuery],) -> bool:
        subscription = TelegramUserSubscriptionService.GetUserActiveSubscription(
            event.from_user.id)

        if subscription:
            # Пользователь с активной подпиской
            limitation_object = TelegramUserSubscriptionService.GetUserLimitations(
                event.from_user.id)
            limits = SUBSCRIPTION_LIMITATIONS
        else:
            # Пользователь без активной подписки
            limitation_object = TelegramUserSubscriptionService.GetUserDailyLimitations(
                event.from_user.id)
            limits = DAILY_LIMITATIONS

        limitation = limitation_object.get('limitations')
        user = limitation_object.get('user')
        if limitation[self.action_type] < limits[self.action_type]:
            print('bas')
            return True
        else:
            await event.answer(
                text=LocalizationService.BotTexts.GetLimitiedText(
                    user.get('language')),
                show_alert=True
            )
            return False
        