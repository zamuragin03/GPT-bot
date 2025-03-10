from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from Keyboards import Keyboard
from Config import SUBSCRIPTION_LIMITATIONS
from Service import TelegramUserService, BotService, TelegramUserSubscriptionService, LocalizationService, AdminService
from aiogram.fsm.context import FSMContext
from aiogram.types.base import TelegramObject
from typing import Union


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) and event.text and event.text.startswith('/start'):
            info_array = event.text.split(' ')
            ref_id = None
            if len(info_array) > 1:
                ref_id = info_array[1]
                current_user = TelegramUserService.GetTelegramUserByExternalId(
                    ref_id)
                new_user = TelegramUserService.GetTelegramUserByExternalId(
                    event.from_user.id)
                if current_user and new_user.get('detail') == 'Not found.':
                    # remove comment if add subscription for both
                    # TelegramUserSubscriptionService.CreateSubscription(
                    #     current_user.get('external_id'), 1)
                    try:
                        local_text = LocalizationService.BotTexts.JoinedByInviteLinkText(
                            current_user.get('language'))
                        await event.bot.send_message(
                            chat_id=current_user.get('external_id'),
                            text=local_text.format(
                                username=event.from_user.username,
                            )
                        )
                    except Exception as e:
                        raise e
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
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            current_user = TelegramUserService.GetTelegramUserByExternalId(
                user.id)
            if current_user:
                subscription_state = await BotService.check_user_subscription(event)
                if subscription_state:
                    return await handler(event, data)
                else:
                    return

        return await handler(event, data)


class CaptchaMiddleWare(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str,    Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data.get("state")
        return await handler(event, data)


class StartBypassMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str,    Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.text.startswith('start'):
            return await handler(event, data)


class GPTSubscriptionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str,    Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]) -> Any:
        subscription = TelegramUserSubscriptionService.GetUserActiveSubscription(
            event.from_user.id)

        if subscription:
            return await handler(event, data)
        else:
            try:
                user = TelegramUserService.GetTelegramUserByExternalId(
                    event.from_user.id)
                langauge = user.get('language', 'ru')
                inactive_text = LocalizationService.BotTexts.GetInactiveSubscriptionText(
                    langauge)
                await event.bot.send_message(
                    event.from_user.id,
                    text=inactive_text,
                    reply_markup=Keyboard.Get_Subscription_Keyboard(langauge)
                )
            except Exception as e:
                print(e)


class BannedMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str,    Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]) -> Any:
        user = TelegramUserService.GetTelegramUserByExternalId(
            event.from_user.id)
        if not user.get('is_banned'):
            return await handler(event, data)
        else:
            await event.bot.send_message(
                    event.from_user.id,
                    text=LocalizationService.BotTexts.GetRestrictedText(user.get('language'))
                )
            return 

class AdminMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str,    Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]) -> Any:
        admins_list = AdminService.GetAllAdminsID()
        if event.from_user.id not in admins_list:
            return
        return await handler(event, data)
