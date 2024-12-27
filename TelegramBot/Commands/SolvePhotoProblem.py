from pyparsing import ParseFatalException
from Config import dp, bot, router
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMAdmin, FSMPhotoProblem
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.enums.parse_mode import ParseMode
from aiogram import types
from Service import CustomFilters
from Service.BotService import BotService
from Service.GPTService import ChatGPTService, DefaultModeGPTService


@router.message(
    FSMPhotoProblem.sending_message,
    F.photo,
    CustomFilters.SubscriberUser()
)
async def handlePhoto(message: types.Message, state: FSMContext):
    thinking_message = await message.answer("Генерирую ответ...")
    await bot.send_chat_action(message.chat.id, action="typing")

    photo = message.photo[-1]
    photo_path = f'./{photo.file_unique_id}.jpg'
    await message.bot.download(file=message.photo[-1].file_id, destination=photo_path)
    base64_img = BotService.encode_image(photo_path)
    caption = message.caption or ""
    response_from_gpt = await ChatGPTService.SolvePhotoProblem(caption, base64_img)
    with open('./code.tex', 'w') as f:
        f.write(response_from_gpt.code)
    try:
        image_to_send = BotService.latex_to_image(
            response_from_gpt.code, message.from_user.id)
        await message.answer_photo(
            caption='Решение вашей задачи',
            photo=image_to_send,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.answer(text='Не получается создать красивый ответ для вас. Отправлю решение текстом')
        data = await state.get_data()
        # Проверка наличия объекта code_helper в состоянии
        default_mode_helper = data.get('default_mode_helper')

        if not default_mode_helper:
            default_mode_helper = DefaultModeGPTService(
                external_id=message.from_user.id)
            await state.update_data(default_mode_helper=default_mode_helper)
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
        except:
            pass
