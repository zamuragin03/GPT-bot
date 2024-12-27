
import asyncio
from Config import dp, bot, router, PATH_TO_TEMP_FILES
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMAdmin, FSMCourseWorkHelper
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.enums.content_type import ContentType
from aiogram import types
from Service import CustomFilters
from Service.BotService import BotService
from Service.GPTService import CourseWorkGPTService
from Service import GOSTWordDocument


@router.message(
    FSMCourseWorkHelper.typing_topic,
    CustomFilters.SubscriberUser()
)
async def handleRequestAbstract(message: types.Message, state: FSMContext):
    data = await state.get_data()
    thinking_message = await message.answer("Придумываю план для твоей работы...")
    await bot.send_chat_action(message.chat.id, action="typing")
    topic = message.text
    # Проверка наличия объекта code_helper в состоянии
    course_service = data.get('course_service')
    if not course_service:
        course_service = CourseWorkGPTService(
            external_id=message.from_user.id, topic=topic)
        await state.update_data(course_service=course_service)
    course_service.get_initial_plan()

    plan = await course_service.get_plan_response()
    await message.answer(
        'Придумал для вашей работы такой план:\n\n• – заголовок 1-го уровня\n•• – заголовок 2-го уровня '
    )
    parsed_plan = BotService.parse_course_work_plan(plan)
    await message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithCourseWorkPlan(data['language'])
    )
    await state.set_state(FSMCourseWorkHelper.choosing_action_with_plan)


@router.callback_query(
    FSMCourseWorkHelper.choosing_action_with_plan,
    F.data == 'genereate_new_plan'
)
async def regenerate_plan(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    thinking_message = await call.message.answer("Придумываю новый план для твоей работы...")
    await bot.send_chat_action(call.message.chat.id, action="typing")
    data = await state.get_data()
    course_service: CourseWorkGPTService = data.get('course_service')
    course_service.regenerate_plan()
    new_plan = await course_service.get_plan_response()
    parsed_plan = BotService.parse_course_work_plan(new_plan)
    await call.message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithCourseWorkPlan(data['language'])
    )
    await state.set_state(FSMCourseWorkHelper.choosing_action_with_plan)


@router.callback_query(
    FSMCourseWorkHelper.choosing_action_with_plan,
    F.data == 'add_details_to_plan'
)
async def regenerate_plan(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        'Напишите, свое для плана вашей курсовой работы в следующем сообщении:',

    )
    await state.set_state(FSMCourseWorkHelper.typing_comments_on_plan)


@router.message(
    FSMCourseWorkHelper.typing_comments_on_plan,
    CustomFilters.SubscriberUser()
)
async def handleRequestAbstract(message: types.Message, state: FSMContext):
    data = await state.get_data()
    comment_on_plan = message.text
    data = await state.get_data()
    thinking_message = await message.answer("Придумываю новый план для твоей работы...")
    await bot.send_chat_action(message.chat.id, action="typing")
    data = await state.get_data()
    course_service: CourseWorkGPTService = data.get('course_service')
    course_service.regenerate_plan_with_user_detail(comment_on_plan)
    new_plan = await course_service.get_plan_response()
    parsed_plan = BotService.parse_course_work_plan(new_plan)
    await message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithCourseWorkPlan(data['language'])
    )
    await state.set_state(FSMCourseWorkHelper.choosing_action_with_plan)

# Функция для обратного отсчета


async def countdown(call, countdown_message, duration=300): 
    for remaining in range(duration, 0, -5): 
        await asyncio.sleep(5) 
        new_text = f"Пишу курсовую работу.\n\nОставшееся время: {remaining // 60} минут {remaining % 60} секунд...\n\n\nЯ отправлю документ по готовности" 
        # Обновляем сообщение только если текст изменился 
        if countdown_message.text != new_text: 
            await countdown_message.edit_text(new_text) 
    await countdown_message.edit_text("Завершаю написание курсовой работы...")


@router.callback_query(
    FSMCourseWorkHelper.choosing_action_with_plan,
    F.data == 'create_course_work'
)
async def regenerate_plan(call: types.CallbackQuery, state: FSMContext):
    countdown_message = await call.message.answer("Пишу курсовую работу.\n\nОставшееся время: 5 минут 0 секунд...\n\n\nЯ отправлю документ по готовности")
    # Запуск обратного отсчета в фоновом режиме
    asyncio.create_task(countdown(call, countdown_message))

    data = await state.get_data()
    course_service: CourseWorkGPTService = data.get('course_service')
    # result = await course_service.build_course_work()
    result = await course_service.build_course_work_mock()

    # doc_creator = GOSTWordDocument(result)
    # doc_creator.create_document()
    # end_path = PATH_TO_TEMP_FILES.joinpath(str(call.from_user.id)).joinpath(
    #     f'Курсовая_работа_{call.message.message_id}.docx')
    # end_path.parent.mkdir(parents=True, exist_ok=True)
    # doc_creator.save_document(end_path)

    await call.message.answer_document(
        # FSInputFile(end_path),
        FSInputFile('/Users/zanuragin03/Desktop/progs/StudyGPT_Bot/TelegramBot/Users_Files/225529144/Курсовая_работа_1765.docx'),
        caption='Ваша готовая курсовая работа:)\nДанная версия не является конечной и требует доработок.\n\n\nНе забудьте добавить титульный лист и оглавление'
    )
