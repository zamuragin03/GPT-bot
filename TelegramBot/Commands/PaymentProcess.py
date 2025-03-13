from Config import dp, bot, router
from Keyboards import Keyboard, KeyboardService
from aiogram import F
from States import (FSMUser,)
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from Service import (LocalizationService,
                     PaymentService,
                     SubscriptionTypeService,
                     TelegramUserSubscriptionService)
import logging
from datetime import datetime
from aiogram import types



@router.callback_query(
    F.data == 'buy',
    FSMUser.choosing_action_with_sub
)
async def buy_subcription(call: types.CallbackQuery, state: FSMContext, ):
    data = await state.get_data()
    payment_text = LocalizationService.BotTexts.GetPaymentText(
        data.get('language','ru'))
    subscription = SubscriptionTypeService.GetSubscriptionByDuration(168)
    payment_service = PaymentService(
        subscription.get('price'), call.from_user.id,)
    payment = payment_service.create_payment()
    payment_text_formatted = payment_text.format(
        order_id=payment_service.order_id,
        item_name=LocalizationService.BotTexts.GetsubscriptionName(
            subscription.get('name'), data.get('language','ru')),
        price=subscription.get('price'),
        created_at=datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
    )
    await call.message.edit_text(
        text=payment_text_formatted,
        reply_markup=Keyboard.GetPaymentKeyboard(
            data.get('language','ru'), payment.confirmation.confirmation_url)
    )
    if await payment_service.check_payment():
        success_payment_text = LocalizationService.BotTexts.GetPaymentStatusText(
            data.get('language','ru'), True)
        await call.message.edit_text(
            success_payment_text,
        )
        TelegramUserSubscriptionService.CreateSubscription(
            call.from_user.id, subscription.get('duration'))
    else:
        invalid_payment_text = LocalizationService.BotTexts.GetPaymentText(
            data.get('language','ru'), False)
        await call.message.answer(
            invalid_payment_text.format(order_id=payment_service.id),
        )
