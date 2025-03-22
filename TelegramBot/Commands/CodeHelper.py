import asyncio
from Config import dp, bot, gpt_router, GROUP_LINK_URL
from Keyboards import Keyboard, KeyboardService
from aiogram import F
from States import FSMCodeHelper
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from Service import LocalizationService, CodeHelperGPTService, CustomFilters, BotService, TelegramUserService

from aiogram.enums.parse_mode import ParseMode
from aiogram import types



# handle message with code helper
@gpt_router.message(
    FSMCodeHelper.typing_message,
    CustomFilters.gptTypeFilter('code_helper')
    
)
async def typing_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    code_helper: CodeHelperGPTService = data.get('code_helper')
    if code_helper.check_if_context_limit_reached():
        await message.reply(
            text=LocalizationService.BotTexts.GetLimitedContextText(data.get('language', 'ru')),
            reply_markup=Keyboard.Code_helper_buttons(data.get('language','ru')),
        )
        return
    code_helper.add_message(message.text)
    result = await BotService.run_with_progress(
        message=message,
        total_time=15,
        task=code_helper.generate_response,
    )
    await BotService.send_long_message(message,
        result,
        reply_markup=Keyboard.Code_helper_buttons(data.get('language','ru')),
        parse_mode=ParseMode.HTML,
    )


@gpt_router.callback_query(
    FSMCodeHelper.typing_message,
    F.data.in_({'auto_save_on', 'auto_save_off'})
)
async def clear_context(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    code_helper: CodeHelperGPTService = data.get('code_helper')
    code_helper.set_auto_save(True if call.data == 'auto_save_on' else False)
    await call.answer(
        LocalizationService.BotTexts.GetCodeHelperAutoSaveText(call.data, data.get('language','ru')),
        reply_markup=Keyboard.Clear_Context_kb(data.get('language','ru')),
        parse_mode=ParseMode.HTML,
        show_alert=True
    )


@gpt_router.callback_query(
    FSMCodeHelper.typing_message,
    F.data == 'clear_context',
)
async def clear_context(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    code_helper: CodeHelperGPTService = data.get('code_helper')
    code_helper.clear_context()
    await call.answer(
        LocalizationService.BotTexts.GetClearContextText(data.get('language','ru')),
        reply_markup=Keyboard.Clear_Context_kb(data.get('language','ru')),
        parse_mode=ParseMode.HTML,
        show_alert=True
    )


@gpt_router.callback_query(
    FSMCodeHelper.typing_message,
    F.data == 'change_reasoning_effort',
)
async def change_reasoning_effort(call: types.CallbackQuery, state: FSMContext):
    user = TelegramUserService.GetTelegramUserByExternalId(call.from_user.id)
    await call.message.answer(
        text=LocalizationService.BotTexts.GetReasoningEffortText(
            user.get('language')),
        reply_markup=Keyboard.Get_Reasoning_Effort_Kb(user.get('language')),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(FSMCodeHelper.choosing_reasoning_effort)


@gpt_router.callback_query(
    FSMCodeHelper.choosing_reasoning_effort,
    F.data.in_(KeyboardService.get_reasoning_options()),
)
async def change_reasoning_effort(call: types.CallbackQuery, state: FSMContext):
    user = TelegramUserService.GetTelegramUserByExternalId(call.from_user.id)
    data = await state.get_data()
    code_helper: CodeHelperGPTService = data.get(
        'code_helper')
    code_helper.change_reasoning_effort(call.data)  
    await call.answer(
        text=LocalizationService.BotTexts.GetCancellationText(
            user.get('language')),
        reply_markup=Keyboard.Get_Reasoning_Effort_Kb(user.get('language')),
        parse_mode=ParseMode.HTML,
        show_alert=True
    )
    await call.message.delete()

