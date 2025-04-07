
import asyncio
from Config import dp, bot, gpt_router,router, PATH_TO_TEMP_FILES, GROUP_LINK_URL
from Keyboards.keyboards import Keyboard, Callbacks
from aiogram import F
from States import FSMUser, FSMCourseWorkHelper
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.enums.content_type import ContentType
from aiogram import types
from Service import CourseWorkGPTService, BotService, GOSTWordDocument, LocalizationService, CustomFilters
import random



@router.callback_query(
    FSMUser.select_mode,
    F.data == 'course_work_helper',
    CustomFilters.gptTypeFilter('course_work_helper')

)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    course_work_text = LocalizationService.BotTexts.GetCourseWorkText(
        data.get('language', 'ru'))

    await call.message.edit_text(
        text=course_work_text,
        reply_markup=Keyboard.GenerateWorkButton(
            call.data, data.get('language', 'ru'))
    )
    await state.set_state(FSMCourseWorkHelper.choosing_action)


@gpt_router.callback_query(
    F.data == 'course_work_helper',
    FSMCourseWorkHelper.choosing_action,
    CustomFilters.gptTypeFilter('course_work_helper')

)
async def start_course_work(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    welcome_text = LocalizationService.BotTexts.GetCourseWorkWelcomeHelperText(
        data.get('language','ru'))
    await call.message.answer(
        welcome_text,
    )
    await state.set_state(FSMCourseWorkHelper.typing_topic)


@gpt_router.message(
    FSMCourseWorkHelper.typing_topic,
)
async def handleRequestAbstract(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(topic=message.text)
    number_of_pages_text = LocalizationService.BotTexts.SelectNumberOfPages(
        data.get('language', 'ru'))
    await message.answer(
        number_of_pages_text,
        reply_markup=Keyboard.NumberOfPages([15, 20, 25, 30, 35, 40, 45])
    )
    await state.set_state(FSMCourseWorkHelper.selecting_pages_number)


@gpt_router.callback_query(
    Callbacks.page_number_callback.filter(),
    FSMCourseWorkHelper.selecting_pages_number
)
async def SelectPageumber(call: types.CallbackQuery, state: FSMContext, callback_data: Callbacks.page_number_callback):
    data = await state.get_data()
    await state.update_data(page_number=callback_data.page_number)
    select_generation_mode = LocalizationService.BotTexts.SelectGenerationMode(
        data.get('language', 'ru'))
    await call.message.answer(
        select_generation_mode,
        reply_markup=Keyboard.PlanType(data.get('language', 'ru'))
    )
    await state.set_state(FSMCourseWorkHelper.choosing_plan_generation)


@gpt_router.callback_query(
    F.data == 'confirm_plan',
    FSMCourseWorkHelper.choosing_action_with_plan
)
async def handleRequestAbstract(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    confirm_plan_text = LocalizationService.BotTexts.GetConfirmPlanText(
        data.get('language','ru'))
    await call.message.answer(
        confirm_plan_text,
        reply_markup=Keyboard.GetConfirmationActions(data.get('language','ru'))
    )
    await state.set_state(FSMCourseWorkHelper.proceed_action)


@gpt_router.callback_query(
    FSMCourseWorkHelper.choosing_action_with_plan,
    F.data == 'genereate_new_plan'
)
async def regenerate_plan(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    course_service: CourseWorkGPTService = data.get('course_service')

    if not course_service.is_retries_allowed():
        await call.answer(
            LocalizationService.BotTexts.RegenerationLimitExceded(
                data.get('language','ru')),
            show_alert=True
        )
        return
    await call.message.edit_text(LocalizationService.BotTexts.CreatingPlanMessage(data.get('language','ru')))
    await bot.send_chat_action(call.message.chat.id, action="typing")
    course_service.regenerate_plan()

    plan = await course_service.get_plan_response()
    await call.message.answer(
        LocalizationService.BotTexts.GetPlanScheme(data.get('language','ru'))
    )
    parsed_plan = BotService.parse_work_plan(plan)
    await call.message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithDonePlan(data.get('language','ru')),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(FSMCourseWorkHelper.choosing_action_with_plan)


@gpt_router.callback_query(
    F.data == 'auto_plan',
    FSMCourseWorkHelper.choosing_plan_generation
)
async def auto_plan(call: types.CallbackQuery, state: FSMContext,):
    data = await state.get_data()
    thinking_message = await call.message.answer(LocalizationService.BotTexts.CreatingPlanMessage(data.get('language','ru')))
    await bot.send_chat_action(call.message.chat.id, action="typing")

    course_service = CourseWorkGPTService(
        external_id=call.from_user.id,
        topic=data['topic'],
        page_number=data['page_number'])
    await state.update_data(course_service=course_service)

    course_service.get_initial_plan()
    plan = await course_service.get_plan_response()

    parsed_plan = BotService.parse_work_plan(plan)
    await call.message.answer(
        LocalizationService.BotTexts.GetPlanScheme(data.get('language','ru'))
    )
    parsed_plan = BotService.parse_work_plan(plan)
    await call.message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithDonePlan(data.get('language','ru')),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(FSMCourseWorkHelper.choosing_action_with_plan)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=thinking_message.message_id)


@gpt_router.callback_query(
    F.data == 'set_plan',
    FSMCourseWorkHelper.choosing_plan_generation
)
async def set_plan(call: types.CallbackQuery, state: FSMContext,):
    data = await state.get_data()
    manual_plan = LocalizationService.BotTexts.GetAbstractManualPlan(
        data.get('language','ru'))
    await call.message.edit_text(manual_plan,)
    await state.set_state(FSMCourseWorkHelper.typing_manual_plan)


@gpt_router.message(
    FSMCourseWorkHelper.typing_manual_plan
)
async def retrieving_manual_plan(message: types.Message, state: FSMContext,):
    data = await state.get_data()
    thinking_message = await message.answer(LocalizationService.BotTexts.CreatingPlanMessage(data.get('language','ru')))
    user_text = message.text
    course_service = data.get('course_service')

    if not course_service:
        course_service = CourseWorkGPTService(
            external_id=message.from_user.id,
            topic=data['topic'],
            page_number=data['page_number'])
        await state.update_data(course_service=course_service)
    course_service.regenerate_plan_with_user_detail(user_text)
    plan = await course_service.get_plan_response()
    parsed_plan = BotService.parse_work_plan(plan)
    await message.answer(
        LocalizationService.BotTexts.GetPlanScheme(data.get('language','ru')),
    )
    await message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithDonePlan(data.get('language','ru'),),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(FSMCourseWorkHelper.choosing_action_with_plan)
    await bot.delete_message(chat_id=message.chat.id, message_id=thinking_message.message_id)




@gpt_router.message(
    FSMCourseWorkHelper.typing_topic,
)
async def handleRequestAbstract(message: types.Message, state: FSMContext):
    data = await state.get_data()
    thinking_message = await message.answer(LocalizationService.BotTexts.CreatingPlanMessage(data.get('language','ru')))
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
    await thinking_message.edit_text(
        LocalizationService.BotTexts.GetPlanScheme(data.get('language','ru'))
    )
    parsed_plan = BotService.parse_work_plan(plan)
    await message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithDonePlan(data.get('language','ru'))
    )
    await state.set_state(FSMCourseWorkHelper.choosing_action_with_plan)
    

@gpt_router.callback_query(
    F.data == 'proceed_generation',
    FSMCourseWorkHelper.proceed_action
)
async def handleRequestAbstract(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    course_service: CourseWorkGPTService = data.get('course_service')
    result = await BotService.run_process_with_countdown(
        message=call.message,
        task=course_service.build_course_work
    )
    doc_creator = GOSTWordDocument(result)
    doc_creator.create_document()
    end_path = PATH_TO_TEMP_FILES.joinpath(str(call.message.from_user.id)).joinpath(
        f'Курсовая_{data["topic"][:25]}_{call.message.message_id}.docx')
    end_path.parent.mkdir(parents=True, exist_ok=True)
    doc_creator.save_document(end_path)
    done_work_text = LocalizationService.BotTexts.DoneWorkText(
        data.get('language', 'ru'))
    await call.message.answer_document(
        FSInputFile(end_path),
        caption=done_work_text,
    )

@gpt_router.callback_query(
    F.data == 'proceed_generation',
    FSMCourseWorkHelper.proceed_action
)
async def handleRequestAbstract(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    course_service: CourseWorkGPTService = data.get('course_service')
    result = await BotService.run_process_with_countdown(
        message=call.message,
        task=course_service.build_course_work
    )
    doc_creator = GOSTWordDocument(result)
    doc_creator.create_document()
    end_path = PATH_TO_TEMP_FILES.joinpath(str(call.message.from_user.id)).joinpath(
        f'Курсовая_{data["topic"][:25]}_{random.randint(1000,2000)}_{call.message.message_id}.docx')
    end_path.parent.mkdir(parents=True, exist_ok=True)
    doc_creator.save_document(end_path)
    done_work_text = LocalizationService.BotTexts.DoneWorkText(
        data.get('language', 'ru'))
    await call.message.answer_document(
        FSInputFile(end_path),
        caption=done_work_text,
    )
    await BotService.go_menu(bot=bot,event=call, state=state, final_state=FSMUser.select_mode )

    
