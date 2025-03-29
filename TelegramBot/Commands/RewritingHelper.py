import asyncio
from Config import dp, bot, gpt_router,router, GROUP_LINK_URL
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMRewritingHelper, FSMUser
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from Service import LocalizationService, RewritingGPTService, BotService, DocumentTypeFilter, CustomFilters

from aiogram.enums.parse_mode import ParseMode
from aiogram import types


# handle message with rewriting helper


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'rewriting_helper'
)
async def rewriting_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Проверка наличия объекта code_helper в состоянии
    rewriting_helper = data.get('rewriting_helper')

    if not rewriting_helper:
        rewriting_helper = RewritingGPTService(external_id=call.from_user.id, language=data.get('language', 'ru'))
        await state.update_data(rewriting_helper=rewriting_helper)
    await call.message.edit_text(
        text=LocalizationService.BotTexts.GetRewritingHelper(
            data.get('language', 'ru')),
        reply_markup=Keyboard.Get_Back_Button(data.get('language', 'ru'))
    )
    await state.set_state(FSMRewritingHelper.sending_document)



@gpt_router.message(
    DocumentTypeFilter(document_types=['txt',]),
    FSMRewritingHelper.sending_document,
    CustomFilters.gptTypeFilter('rewriting_helper')
)
async def handle_txt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    content = await BotService.GetTXTFileContent(bot, message)
    rewriting_helper: RewritingGPTService = data.get('rewriting_helper')
    rewriting_helper.add_message(content)
    result = await BotService.run_process_with_countdown(
        message=message,
        task=rewriting_helper.generate_response  # Задача
    )
    result_file = await BotService.WriteFileToTXT(result, message.from_user.id)
    await message.answer_document(
        document=result_file,
        caption=LocalizationService.BotTexts.GetRewritingDone(
            data.get('language', 'ru')),
        parse_mode=ParseMode.HTML,
    )


@gpt_router.message(
    DocumentTypeFilter(document_types=['doc', 'docx']),
    FSMRewritingHelper.sending_document,
    CustomFilters.gptTypeFilter('rewriting_helper')

)
async def handle_txt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    content = await BotService.GetWordFileContent(bot, message)
    rewriting_helper: RewritingGPTService = data.get('rewriting_helper')
    rewriting_helper.add_message(content)
    result = await BotService.run_process_with_countdown(
        message=message,
        task=rewriting_helper.generate_response  # Задача
    )
    result_file = await BotService.WriteFileToDOCX(result, message.from_user.id)
    await message.answer_document(
        document=result_file,
        caption=LocalizationService.BotTexts.GetRewritingDone(
            data.get('language', 'ru')),
        parse_mode=ParseMode.HTML,
    )
