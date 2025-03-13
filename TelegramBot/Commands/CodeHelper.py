import asyncio
from Config import dp, bot, gpt_router, GROUP_LINK_URL
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMCodeHelper
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from Service import LocalizationService, CodeHelperGPTService, CustomFilters, BotService

from aiogram.enums.parse_mode import ParseMode
from aiogram import types



# handle message with code helper
@gpt_router.message(
    FSMCodeHelper.typing_message,
    CustomFilters.gptTypeFilter('code_helper')
    
)
async def typing_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    typing_text = LocalizationService.BotTexts.GenerationTextByWorkType(data.get('language','ru'), 'code', 'start')
    demand_minutes, demand_seconds = 0, 10
    finish_text = LocalizationService.BotTexts.GenerationTextByWorkType(data.get('language','ru'), 'code', 'finish')
    countdown_message = await message.answer(typing_text.format(
        minutes=demand_minutes,
        seconds=demand_seconds,
        url=GROUP_LINK_URL
    ),parse_mode=ParseMode.HTML)
    countdown_task = asyncio.create_task(
        BotService.countdown(call=None,
                             countdown_message=countdown_message, duration=demand_minutes*60+demand_seconds, interval=1,
                             new_text=typing_text, finish_text=finish_text))
    code_helper: CodeHelperGPTService = data.get('code_helper')
    response = await code_helper.generate_response(message.text)
    await message.answer(
        response,
        reply_markup=Keyboard.Code_helper_buttons(data.get('language','ru')),
        parse_mode=ParseMode.MARKDOWN,
    )
    countdown_task.cancel()
    try:
        await countdown_message.delete()
    except Exception as e:
        pass


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
        parse_mode=ParseMode.MARKDOWN,
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
        parse_mode=ParseMode.MARKDOWN,
        show_alert=True
    )
