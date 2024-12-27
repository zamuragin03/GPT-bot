from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from Keyboards import Keyboard
from Service import TelegramUserService, BotService
from aiogram.fsm.context import FSMContext
from aiogram.types.base import TelegramObject


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str,    Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.text is not None:
            info_array = event.text.split(' ')
            ref_id = None
            if len(info_array) > 1:
                ref_id = info_array[1]
            TelegramUserService.CreateTelegramUser(
                external_id=event.from_user.id,
                username=event.from_user.username,
                first_name=event.from_user.first_name,
                second_name=event.from_user.last_name,
                ref_external_id=ref_id
            )
            subscription_state = await BotService.check_user_subscription(event)
            if subscription_state:
                return await handler(event, data)
            else:
                return
        else:
            return await handler(event, data)


class CaptchaMiddleWare:
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str,    Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data.get("state")
        return await handler(event, data)
