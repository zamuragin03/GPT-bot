
from aiogram.enums.content_type import ContentType
from Config import dp, bot, router
from Keyboards.keyboards import Keyboard
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from Service import LocalizationService, CodeHelperGPTService, DefaultModeGPTService, BotService, CustomFilters
from aiogram import types
from aiogram.enums.parse_mode import ParseMode
BotTexts = LocalizationService.BotTexts


# handle message with code helper
@router.message(
    F.photo,
    CustomFilters.SubscriberUser()
)
async def get_photo(message: types.Message, state: FSMContext):
    thinking_message = await message.answer("Генерирую ответ...")

    await bot.send_chat_action(message.chat.id, action="typing")
    
    data = await state.get_data()
    # Проверка наличия объекта code_helper в состоянии
    default_mode_helper = data.get('default_mode_helper')

    if not default_mode_helper:
        default_mode_helper = DefaultModeGPTService(
            external_id=message.from_user.id)
        await state.update_data(default_mode_helper=default_mode_helper)
    photo = message.photo[-1]
    photo_path = f'./{photo.file_unique_id}.jpg'
    await message.bot.download(file=message.photo[-1].file_id, destination=photo_path)
    base64_img = BotService.encode_image(photo_path)
    caption = message.caption or ""
    default_mode_helper.add_message_with_attachement(base64_img, caption)
    response = await default_mode_helper.generate_response()
    
    try:
        await message.answer(
        response,
        parse_mode=ParseMode.MARKDOWN
    )
        await bot.delete_message(chat_id=message.chat.id, message_id=thinking_message.message_id)
    except Exception as e:
        print(e)


@router.message(
    F.text,
    ~F.text.startswith('/'),
    CustomFilters.SubscriberUser()
)
async def get_text(message: types.Message, state: FSMContext):
    thinking_message = await message.answer("Генерирую ответ...")
    await bot.send_chat_action(message.chat.id, action="typing")
    
    data = await state.get_data()

    default_mode_helper = data.get('default_mode_helper')

    if not default_mode_helper:
        default_mode_helper = DefaultModeGPTService(message.from_user.id)
        await state.update_data(default_mode_helper=default_mode_helper)


    default_mode_helper.add_message(message.text)
    response = await default_mode_helper.generate_response()

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=thinking_message.message_id)
    except:
        pass

    try:
        await message.answer(
            response,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.answer(response)
