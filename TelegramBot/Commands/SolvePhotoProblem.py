import asyncio
from Config import dp, bot, gpt_router, router, GROUP_LINK_URL, PATH_TO_DOWNLOADED_FILES
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMPhotoProblem, FSMUser
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.enums.parse_mode import ParseMode
from aiogram import types
from Service import SolvePhotoGPTService, DefaultModeGPTService, LocalizationService, BotService, CustomFilters


# handle message with image issue solve
@router.callback_query(
    FSMUser.select_mode,
    F.data == 'photo_issue_helper',
    CustomFilters.gptTypeFilter('photo_issue_helper')
)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    welcome_text = LocalizationService.BotTexts.GetPhotoSolverWelcomeMessage(
        data.get('language', 'ru'))
    await call.message.edit_text(
        text=welcome_text,
        reply_markup=Keyboard.Get_Back_Button(data.get('language', 'ru'))
    )
    await state.set_state(FSMPhotoProblem.sending_message)


@gpt_router.message(
    FSMPhotoProblem.sending_message,
    F.photo,
    CustomFilters.gptTypeFilter('photo_issue_helper')
)
async def handlePhoto(message: types.Message, state: FSMContext):
    data = await state.get_data()
    base64_img = await BotService.encode_image(message)
    caption = message.caption or ""
    photo_solver = SolvePhotoGPTService(
        external_id=message.from_user.id,
    )
    photo_solver.add_message(caption, base64_img)
    result = await BotService.run_process_with_countdown(
        message=message,
        task=photo_solver.generate_response  # Задача
    )
    solution_text = LocalizationService.BotTexts.GetPhotoSolverSolutionMessage(
        data.get('language', 'ru'))
    try:
        image_to_send = BotService.latex_to_image(
            result.code, message.from_user.id)
        await message.answer_photo(
            caption=solution_text,
            photo=image_to_send,
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        print(e)
        await message.answer(text='trying another way')
        # Проверка наличия объекта code_helper в состоянии
        default_mode_helper = data.get('default_mode_helper')

        if not default_mode_helper:
            default_mode_helper = DefaultModeGPTService(
                external_id=message.from_user.id, language=data.get('language', 'ru'))
            await state.update_data(default_mode_helper=default_mode_helper)

        default_mode_helper.add_message_with_attachement(base64_img, caption)
        response = await default_mode_helper.generate_response()
        try:
            await message.answer(
                response,
            )
        except:
            pass
