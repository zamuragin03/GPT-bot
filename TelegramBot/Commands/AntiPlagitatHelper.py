
import asyncio
from Config import dp, bot, router, gpt_router, GROUP_LINK_URL
from Keyboards import Keyboard, KeyboardService
from aiogram import F
from States import FSMAntiplagitHelper, FSMUser
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from Service import LocalizationService, AntiplagiatService, CustomFilters, BotService, TelegramUserService

from aiogram.enums.parse_mode import ParseMode
from aiogram import types


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'antiplagiat_helper',
    CustomFilters.gptTypeFilter('antiplagiat_helper')
)
async def antiplagiat_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    abstract_helper_text = LocalizationService.BotTexts.GetAntiPlagiatText(
        data.get('language', 'ru'))
    await call.message.edit_text(
        text=abstract_helper_text,
        reply_markup=Keyboard.Get_Back_Button(data.get('language', 'ru'))
    )
    await state.set_state(FSMAntiplagitHelper.choosing_action)


# handle message with code helper
@gpt_router.message(
    FSMAntiplagitHelper.choosing_action,
    CustomFilters.gptTypeFilter('antiplagiat_helper'),
    F.document,
)
async def get_document(message: types.Message, state: FSMContext):
    document_path = await BotService.download_file(bot, message)
    service = AntiplagiatService(path_to_file=document_path, external_id=message.from_user.id)
    await service.proceed_document()
    result = await BotService.run_process_with_countdown(
        message=message,
        task=service.check_document,
        phrases=[
            "Проверяю документ на уникальность...",
            "Сравниваю с базой данных...",
            "Ищу совпадения и дубликаты...",
            "Анализирую текст на плагиат...",
            "Подготавливаю отчет...",
            "Проводится глубокий анализ содержания...",
        ]
    )
    data = await state.get_data()
    done_text = LocalizationService.BotTexts.GetAntiPlagiatDoneText(
        data.get('language', 'ru'))
    await message.answer(
        done_text,
        reply_markup=Keyboard.Get_Result_Button(
            selected_language=data.get('language', 'ru'),
            result_url=result
        )
    )
    await BotService.go_menu(bot=bot,event=message, state=state, final_state=FSMUser.select_mode )
    
