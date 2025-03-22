import asyncio
from aiogram.enums.content_type import ContentType
from Config import dp, bot, gpt_free_router, GROUP_LINK_URL, PATH_TO_DOWNLOADED_FILES
from Keyboards import Keyboard, KeyboardService
from aiogram import F
from aiogram.fsm.context import FSMContext
from States import FSMUser, FSMAdmin
from aiogram.filters import *
from Service import LocalizationService, DefaultModeGPTService, BotService, TelegramUserService, CustomFilters
from aiogram import types
from aiogram.enums.parse_mode import ParseMode


@gpt_free_router.message(
    F.photo,
    CustomFilters.gptTypeFilter('default_mode'),
)
async def get_photo(message: types.Message, state: FSMContext):
    user = TelegramUserService.GetTelegramUserByExternalId(
        message.from_user.id)

    data = await state.get_data()
    # Проверка наличия объекта code_helper в состоянии
    default_mode_helper = data.get('default_mode_helper')

    if not default_mode_helper:
        default_mode_helper = DefaultModeGPTService(
            external_id=message.from_user.id)
        await state.update_data(default_mode_helper=default_mode_helper)
    if default_mode_helper.check_if_context_limit_reached():
        await message.reply(
            text=LocalizationService.BotTexts.GetLimitedContextText(user.get('language', 'ru')),
            reply_markup=Keyboard.Code_helper_buttons(user.get('language','ru'))
        )
        return
        
    photo = message.photo[-1]
    photo_folder = PATH_TO_DOWNLOADED_FILES.joinpath(str(message.from_user.id))
    photo_folder.mkdir(parents=True, exist_ok=True)
    photo_path = photo_folder.joinpath(f'{photo.file_unique_id}.jpg')

    await message.bot.download(file=message.photo[-1].file_id, destination=photo_path)
    base64_img = BotService.encode_image(photo_path)
    caption = message.caption or ""
    default_mode_helper.add_message_with_attachement(base64_img, caption)
    result = await BotService.run_with_progress(
        message=message,
        total_time=15,
        task=default_mode_helper.generate_response
    )
    await BotService.send_long_message(message,
        result,
        reply_markup=Keyboard.Code_helper_buttons(user.get('language','ru')),
        parse_mode=ParseMode.HTML,
    )

@gpt_free_router.message(
    CustomFilters.gptTypeFilter('default_mode'),
    F.text,
    ~F.text.startswith('/'),
    
)
async def get_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    default_mode_helper = data.get('default_mode_helper')
    if not default_mode_helper:
        default_mode_helper = DefaultModeGPTService(message.from_user.id)
        await state.update_data(default_mode_helper=default_mode_helper)

    default_mode_helper.add_message(message.text)
    result = await BotService.run_with_progress(
        message=message,
        total_time=15,
        task=default_mode_helper.generate_response
    )
    await BotService.send_long_message(message,
        result,
        parse_mode=ParseMode.HTML,
    )


@gpt_free_router.callback_query(
    F.data.in_({'auto_save_on', 'auto_save_off'}),

)
async def auto_save(call: types.CallbackQuery, state: FSMContext):
    user = TelegramUserService.GetTelegramUserByExternalId(call.from_user.id)
    data = await state.get_data()
    default_mode_helper: DefaultModeGPTService = data.get(
        'default_mode_helper')
    default_mode_helper.set_auto_save(
        True if call.data == 'auto_save_on' else False)
    await call.answer(
        text=LocalizationService.BotTexts.GetCodeHelperAutoSaveText(
            call.data, user.get('language')),
        reply_markup=Keyboard.Clear_Context_kb(user.get('language')),
        parse_mode=ParseMode.HTML,
        show_alert=True
    )


@gpt_free_router.callback_query(
    F.data == 'clear_context',
)
async def clear_context(call: types.CallbackQuery, state: FSMContext):
    user = TelegramUserService.GetTelegramUserByExternalId(call.from_user.id)
    data = await state.get_data()
    default_mode_helper: DefaultModeGPTService = data.get(
        'default_mode_helper')
    default_mode_helper.clear_context()
    await call.answer(
        text=LocalizationService.BotTexts.GetClearContextText(
            user.get('language')),
        reply_markup=Keyboard.Clear_Context_kb(user.get('language')),
        parse_mode=ParseMode.HTML,
        show_alert=True
    )


@gpt_free_router.callback_query(
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
    await state.set_state(FSMUser.choosing_reasoning_effort)


@gpt_free_router.callback_query(
    FSMUser.choosing_reasoning_effort,
    F.data.in_(KeyboardService.get_reasoning_options()),
)
async def change_reasoning_effort(call: types.CallbackQuery, state: FSMContext):
    user = TelegramUserService.GetTelegramUserByExternalId(call.from_user.id)
    data = await state.get_data()
    default_mode_helper: DefaultModeGPTService = data.get(
        'default_mode_helper')
    default_mode_helper.change_reasoning_effort(call.data)  
    await call.answer(
        text=LocalizationService.BotTexts.GetCancellationText(
            user.get('language')),
        reply_markup=Keyboard.Get_Reasoning_Effort_Kb(user.get('language')),
        parse_mode=ParseMode.HTML,
        show_alert=True
    )
    await call.message.delete()
