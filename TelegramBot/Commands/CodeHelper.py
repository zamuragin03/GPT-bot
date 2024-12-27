from Config import dp, bot, router
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMCodeHelper
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from Service import LocalizationService, CodeHelperGPTService, CustomFilters

from aiogram.enums.parse_mode import ParseMode
from aiogram import types

ADMINS = [225529144]
BotTexts = LocalizationService.BotTexts


# handle message with code helper
@router.message(
    FSMCodeHelper.typing_message,
    CustomFilters.SubscriberUser()
)
async def typing_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    code_helper: CodeHelperGPTService = data.get('code_helper')
    response = await code_helper.generate_response(message.text)
    with open('./resp.txt', 'w') as f:
        f.write(response)
    await message.answer(
        response,
        reply_markup=Keyboard.Clear_Context_kb(data['language']),
        parse_mode=ParseMode.MARKDOWN,
    )


@router.callback_query(
    FSMCodeHelper.typing_message,
    F.data == 'clear_context',
)
async def clear_context(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.answer(
        BotTexts.GetClearContextText(data['language']),
        reply_markup=Keyboard.Clear_Context_kb(data['language']),
        parse_mode=ParseMode.MARKDOWN,
        show_alert=True
    )