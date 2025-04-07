from aiogram.filters import Filter
from aiogram import types
from Service import TelegramUserSubscriptionService, LocalizationService
from Config import SUBSCRIPTION_LIMITATIONS, DAILY_LIMITATIONS
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
        if isinstance(event, types.callback_query.CallbackQuery):
            user_id = event.from_user.id
        elif isinstance(event, types.message.Message):
            user_id = event.from_user.id
        subscription = TelegramUserSubscriptionService.GetUserActiveSubscription(
            user_id
        )
        print(f'user_id from filter {self.action_type}',user_id)
        if subscription:
            limitation_object, limits = self._get_limitations(
                TelegramUserSubscriptionService.GetUserLimitations(user_id),
                SUBSCRIPTION_LIMITATIONS
            )
        else:
            limitation_object, limits = self._get_limitations(
                TelegramUserSubscriptionService.GetUserDailyLimitations(
                    user_id),
                DAILY_LIMITATIONS
            )
        
        if not limitation_object:
            return await self._handle_limit_exceeded(event, user_language=None)

        limitation = limitation_object.get('limitations')
        user = limitation_object.get('user')

        if limitation[self.action_type] < limits[self.action_type]:
            return True
        else:
            return await self._handle_limit_exceeded(event, user.get('language'))

    def _get_limitations(self, limitation_object, limits):
        return limitation_object, limits

    async def _handle_limit_exceeded(self, event, user_language):
        message = LocalizationService.BotTexts.GetLimitiedText(user_language if user_language else "ru")
        await event.answer(
            text=message,
            show_alert=True
        )
        return False

class PinFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        print('pin filter')
        return message.pinned_message is not None
    