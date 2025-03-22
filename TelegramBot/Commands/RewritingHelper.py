import asyncio
from Config import dp, bot, gpt_router, GROUP_LINK_URL
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMRewritingHelper
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from Service import LocalizationService, RewritingGPTService, BotService, DocumentTypeFilter, CustomFilters

from aiogram.enums.parse_mode import ParseMode
from aiogram import types



@gpt_router.message(
    DocumentTypeFilter(document_types=['txt',]),
    FSMRewritingHelper.sending_document,
    CustomFilters.gptTypeFilter('rewriting_helper')
)
async def handle_txt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    content = await BotService.GetTXTFileContent(bot, message)
    rewriting_helper: RewritingGPTService = data.get('rewriting_helper')
    typing_text = LocalizationService.BotTexts.GenerationTextByWorkType(data.get('language','ru'), 'rewriting', 'start')
    demand_minutes, demand_seconds = 0, 35
    finish_text = LocalizationService.BotTexts.GenerationTextByWorkType(data.get('language','ru'), 'rewriting', 'finish')
    countdown_message = await message.answer(typing_text.format(
        minutes=demand_minutes,
        seconds=demand_seconds,
        url=GROUP_LINK_URL
    ),parse_mode=ParseMode.HTML)
    countdown_task = asyncio.create_task(
        BotService.countdown(call=None,
                             countdown_message=countdown_message,
                             duration=demand_minutes*60+demand_seconds,
                             interval=2,
                             new_text=typing_text,
                             finish_text=finish_text)
    )
    response = await rewriting_helper.generate_response(content)
    result_file = await BotService.WriteFileToTXT(response, message.from_user.id)
    countdown_task.cancel()
    try:
        await countdown_message.delete()
    except Exception as e:
        pass
    await message.answer_document(
        document=result_file,
        caption=LocalizationService.BotTexts.GetRewritingDone(data.get('language','ru')),
        reply_markup=Keyboard.Clear_Context_kb(data.get('language','ru')),
        parse_mode=ParseMode.HTML,
    )


@gpt_router.message(
    DocumentTypeFilter(document_types=['doc','docx']),
    FSMRewritingHelper.sending_document,
    CustomFilters.gptTypeFilter('rewriting_helper')
    
)
async def handle_txt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    content = await BotService.GetWordFileContent(bot, message)
    rewriting_helper: RewritingGPTService = data.get('rewriting_helper')
    response = await rewriting_helper.generate_response(content)
    result_file = await BotService.WriteFileToDOCX(response, message.from_user.id)
    await message.answer_document(
        document=result_file,
        caption=LocalizationService.BotTexts.GetRewritingDone(data.get('language','ru')),
        reply_markup=Keyboard.Clear_Context_kb(data.get('language','ru')),
        parse_mode=ParseMode.HTML,
    )


@gpt_router.callback_query(
    FSMRewritingHelper.sending_document,
    F.data == 'clear_context',
)
async def clear_context(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    rewriting_helper: RewritingGPTService = data.get('rewriting_helper')
    rewriting_helper.clear_context()
    await call.answer(
        LocalizationService.BotTexts.GetClearContextText(data.get('language','ru')),
        reply_markup=Keyboard.Clear_Context_kb(data.get('language','ru')),
        parse_mode=ParseMode.HTML,
        show_alert=True
    )
