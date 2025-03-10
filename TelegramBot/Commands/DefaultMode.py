import asyncio
from aiogram.enums.content_type import ContentType
from Config import dp, bot, gpt_free_router, GROUP_LINK_URL, PATH_TO_DOWNLOADED_FILES
from Keyboards.keyboards import Keyboard
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from Service import LocalizationService, DefaultModeGPTService, BotService, TelegramUserService, CustomFilters
from aiogram import types
from aiogram.enums.parse_mode import ParseMode


@gpt_free_router.message(
    F.photo,
    CustomFilters.gptTypeFilter('default_mode')
)
async def get_photo(message: types.Message, state: FSMContext):
    user = TelegramUserService.GetTelegramUserByExternalId(
        message.from_user.id)
    typing_text = LocalizationService.BotTexts.GenerationTextByWorkType(
        user.get('language'), 'default_mode_photo', 'start')
    demand_minutes, demand_seconds = 0, 20
    finish_text = LocalizationService.BotTexts.GenerationTextByWorkType(
        user.get('language'), 'default_mode_photo', 'finish')
    countdown_message = await message.answer(typing_text.format(
        minutes=demand_minutes,
        seconds=demand_seconds,
        url=GROUP_LINK_URL
    ), parse_mode=ParseMode.HTML,
    reply_markup=Keyboard.Code_helper_buttons(user.get('language')))
    countdown_task = asyncio.create_task(
        BotService.countdown(call=None,
                             countdown_message=countdown_message,
                             duration=demand_minutes*60+demand_seconds,
                             interval=1,
                             new_text=typing_text,
                             finish_text=finish_text)
    )

    await bot.send_chat_action(message.chat.id, action="typing")

    data = await state.get_data()
    # Проверка наличия объекта code_helper в состоянии
    default_mode_helper = data.get('default_mode_helper')

    if not default_mode_helper:
        default_mode_helper = DefaultModeGPTService(
            external_id=message.from_user.id)
        await state.update_data(default_mode_helper=default_mode_helper)
    photo = message.photo[-1]
    photo_folder = PATH_TO_DOWNLOADED_FILES.joinpath(str(message.from_user.id))
    photo_folder.mkdir(parents=True, exist_ok=True)
    photo_path = photo_folder.joinpath(f'{photo.file_unique_id}.jpg')

    await message.bot.download(file=message.photo[-1].file_id, destination=photo_path)
    base64_img = BotService.encode_image(photo_path)
    caption = message.caption or ""
    default_mode_helper.add_message_with_attachement(base64_img, caption)
    response = await default_mode_helper.generate_response()

    try:
        await countdown_message.edit_text(
            response,
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboard.Code_helper_buttons(user.get('language')),

        )
    except Exception as e:
        print(e)
        # Завершаем задачу обратного отсчета и удаляем сообщение
    countdown_task.cancel()


@gpt_free_router.message(
    CustomFilters.gptTypeFilter('default_mode'),
    F.text,
    ~F.text.startswith('/'),
)
async def get_text(message: types.Message, state: FSMContext):
    user = TelegramUserService.GetTelegramUserByExternalId(
        message.from_user.id)
    typing_text = LocalizationService.BotTexts.GenerationTextByWorkType(
        user.get('language'), 'default_mode_text', 'start')
    demand_minutes, demand_seconds = 0, 20
    finish_text = LocalizationService.BotTexts.GenerationTextByWorkType(
        user.get('language'), 'default_mode_text', 'finish')
    countdown_message = await message.answer(typing_text.format(
        minutes=demand_minutes,
        seconds=demand_seconds,
        url=GROUP_LINK_URL
    ), parse_mode=ParseMode.HTML)
    countdown_task = asyncio.create_task(
        BotService.countdown(call=None,
                             countdown_message=countdown_message,
                             duration=demand_minutes*60+demand_seconds,
                             interval=1,
                             new_text=typing_text,
                             finish_text=finish_text)
    )
    await bot.send_chat_action(message.chat.id, action="typing")

    data = await state.get_data()

    default_mode_helper = data.get('default_mode_helper')

    if not default_mode_helper:
        default_mode_helper = DefaultModeGPTService(message.from_user.id)
        await state.update_data(default_mode_helper=default_mode_helper)

    default_mode_helper.add_message(message.text)
    response = await default_mode_helper.generate_response()
    try:
        await countdown_message.edit_text(
            response,
            reply_markup=Keyboard.Code_helper_buttons(user.get('language')),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print(e)

        await message.answer(response)

    countdown_task.cancel()


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
