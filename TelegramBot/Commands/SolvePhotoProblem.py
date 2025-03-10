import asyncio
from Config import dp, bot, gpt_router, GROUP_LINK_URL, PATH_TO_DOWNLOADED_FILES
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMAdmin, FSMPhotoProblem
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.enums.parse_mode import ParseMode
from aiogram import types
from Service import SolvePhotoGPTService, DefaultModeGPTService, LocalizationService, BotService, CustomFilters


@gpt_router.message(
    FSMPhotoProblem.sending_message,
    F.photo,
    CustomFilters.gptTypeFilter('photo_issue_helper')
)
async def handlePhoto(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await bot.send_chat_action(message.chat.id, action="typing")
    typing_text = LocalizationService.BotTexts.GenerationTextByWorkType(
        data['language'], 'photo_math', 'start')
    demand_minutes, demand_seconds = 0, 35
    finish_text = LocalizationService.BotTexts.GenerationTextByWorkType(
        data['language'], 'photo_math', 'finish')
    countdown_message = await message.answer(typing_text.format(
        minutes=demand_minutes,
        seconds=demand_seconds,
        url=GROUP_LINK_URL
    ), parse_mode=ParseMode.HTML)
    countdown_task = asyncio.create_task(
        BotService.countdown(call=None,
                             countdown_message=countdown_message,
                             duration=demand_minutes*60+demand_seconds,
                             interval=2,
                             new_text=typing_text,
                             finish_text=finish_text)
    )
    photo = message.photo[-1]
    photo_folder = PATH_TO_DOWNLOADED_FILES.joinpath(str(message.from_user.id))
    photo_folder.mkdir(parents=True, exist_ok=True)
    photo_path = photo_folder.joinpath(f'{photo.file_unique_id}.jpg')
    await message.bot.download(file=message.photo[-1].file_id, destination=photo_path)
    base64_img = BotService.encode_image(photo_path)
    caption = message.caption or ""
    response_from_gpt = await SolvePhotoGPTService.SolvePhotoProblem(caption, base64_img)
    try:
        image_to_send = BotService.latex_to_image(
            response_from_gpt.code, message.from_user.id)
        await message.answer_photo(
            caption='Solution:',
            photo=image_to_send,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.answer(text='trying another way')
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
        except:
            pass
    countdown_task.cancel()
    try:
        await countdown_message.delete()
    except Exception as e:
        pass
