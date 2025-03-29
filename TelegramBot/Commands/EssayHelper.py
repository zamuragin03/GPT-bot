
import asyncio
from Config import dp, bot, gpt_router, router, PATH_TO_TEMP_FILES, GROUP_LINK_URL
from Keyboards.keyboards import Keyboard, Callbacks
from aiogram import F
from States import FSMEssayhelper, FSMUser
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.enums.content_type import ContentType
from aiogram import types
from Service import LocalizationService
from Service import BotService, EssayGPTService, CustomFilters,GOSTWordEssayDocument


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'essay_helper',
    CustomFilters.gptTypeFilter('essay_helper')
)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    abstract_helper_text = LocalizationService.BotTexts.GetEssayWelcomeHelperText(
        data.get('language', 'ru'))
    await call.message.edit_text(
        text=abstract_helper_text,
        reply_markup=Keyboard.GenerateWorkButton(
            call.data, data.get('language', 'ru'))
    )
    await state.set_state(FSMEssayhelper.choosing_action)


@gpt_router.callback_query(
    FSMEssayhelper.choosing_action,
    F.data == 'essay_helper'
)
async def StatWriting(call: types.CallbackQuery, state: FSMContext, ):
    data = await state.get_data()
    abstarct_topic_request_text = LocalizationService.BotTexts.GetEssayHelperText(
        data.get('language', 'ru'))
    await call.message.answer(
        abstarct_topic_request_text,
    )
    await state.set_state(FSMEssayhelper.typing_topic)


@gpt_router.message(
    FSMEssayhelper.typing_topic,
)
async def handleRequestAbstract(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(topic=message.text)
    number_of_pages_text = LocalizationService.BotTexts.SelectNumberOfPages(
        data.get('language', 'ru'))
    await message.answer(
        number_of_pages_text,
        reply_markup=Keyboard.NumberOfPages([3, 5, 7, 10])
    )
    await state.set_state(FSMEssayhelper.selecting_pages_number)


@gpt_router.callback_query(
    Callbacks.page_number_callback.filter(),
    FSMEssayhelper.selecting_pages_number
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
    await state.set_state(FSMEssayhelper.choosing_plan_generation)


@gpt_router.callback_query(
    F.data == 'set_plan',
    FSMEssayhelper.choosing_plan_generation
)
@gpt_router.callback_query(
    F.data == 'regenerate',
    FSMEssayhelper.choosing_action_with_plan

)
async def set_plan(call: types.CallbackQuery, state: FSMContext,):
    data = await state.get_data()
    manual_plan = LocalizationService.BotTexts.GetAbstractManualPlan(
        data.get('language', 'ru'))
    await call.message.edit_text(manual_plan,)
    await state.set_state(FSMEssayhelper.typing_manual_plan)


@gpt_router.message(
    FSMEssayhelper.typing_manual_plan
)
async def retrieving_manual_plan(message: types.Message, state: FSMContext,):
    data = await state.get_data()
    thinking_message = await message.answer(LocalizationService.BotTexts.CreatingPlanMessage(data.get('language', 'ru')))
    user_text = message.text
    essay_service = data.get('essay_service')

    if not essay_service:
        essay_service = EssayGPTService(
            external_id=message.from_user.id,
            topic=data['topic'],
            page_number=data['page_number'])
        await state.update_data(essay_service=essay_service)
    essay_service.regenerate_plan_with_user_detail(user_text)
    plan = await essay_service.get_plan_response()
    parsed_plan = BotService.parse_work_plan(plan)
    await message.answer(
        LocalizationService.BotTexts.GetPlanScheme(data.get('language', 'ru'))
    )
    await message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithDonePlan(data.get('language', 'ru'),),
        parse_mode=ParseMode.HTML
    )
    await bot.delete_message(chat_id=message.chat.id, message_id=thinking_message.message_id)
    await state.set_state(FSMEssayhelper.choosing_action_with_plan)


@gpt_router.callback_query(
    F.data == 'auto_plan',
    FSMEssayhelper.choosing_plan_generation
)
async def auto_plan(call: types.CallbackQuery, state: FSMContext,):
    thinking_message = await call.message.answer(LocalizationService.BotTexts.CreatingPlanMessage(data.get('language', 'ru')))
    await bot.send_chat_action(call.message.chat.id, action="typing")

    data = await state.get_data()
    essay_service = EssayGPTService(
        external_id=call.from_user.id,
        topic=data['topic'],
        page_number=data['page_number'])
    await state.update_data(essay_service=essay_service)

    essay_service.get_initial_plan()
    plan = await essay_service.get_plan_response()

    parsed_plan = BotService.parse_work_plan(plan)
    await call.message.answer(
        LocalizationService.BotTexts.GetPlanScheme(data.get('language', 'ru'))
    )
    parsed_plan = BotService.parse_work_plan(plan)
    await call.message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithDonePlan(data.get('language', 'ru')),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(FSMEssayhelper.choosing_action_with_plan)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=thinking_message.message_id)


@gpt_router.callback_query(
    F.data == 'genereate_new_plan',
    FSMEssayhelper.choosing_action_with_plan
)
async def handleRequestAbstract(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    essay_service: EssayGPTService = data.get('essay_service')

    if not essay_service.is_retries_allowed():
        await call.answer(
            LocalizationService.BotTexts.RegenerationLimitExceded(
                data.get('language', 'ru')),
            show_alert=True
        )
        return
    await call.message.edit_text("Придумываю новый план для твоей работы...")
    await bot.send_chat_action(call.message.chat.id, action="typing")
    essay_service.regenerate_plan()

    plan = await essay_service.get_plan_response()
    await call.message.answer(
        LocalizationService.BotTexts.GetPlanScheme(data.get('language', 'ru'))
    )
    parsed_plan = BotService.parse_work_plan(plan)
    await call.message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithDonePlan(data.get('language', 'ru')),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(FSMEssayhelper.choosing_action_with_plan)


@gpt_router.callback_query(
    F.data == 'confirm_plan',
    FSMEssayhelper.choosing_action_with_plan
)
async def handleRequestAbstract(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    confirm_plan_text = LocalizationService.BotTexts.GetConfirmPlanText(
        data.get('language', 'ru'))
    await call.message.answer(
        confirm_plan_text,
        reply_markup=Keyboard.GetConfirmationActions(
            data.get('language', 'ru'))
    )
    await state.set_state(FSMEssayhelper.proceed_action)


@gpt_router.callback_query(
    F.data == 'proceed_generation',
    FSMEssayhelper.proceed_action
)
async def handleRequestAbstract(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    essay_service: EssayGPTService = data.get('essay_service')
    
    result = await BotService.run_process_with_countdown(
        message=call.message,
        task=essay_service.build_essay_work
    )
    doc_creator = GOSTWordEssayDocument(result)
    doc_creator.create_document()
    end_path = PATH_TO_TEMP_FILES.joinpath(str(call.message.from_user.id)).joinpath(
        f'Essay_{data["topic"][:25]}_{call.message.message_id}.docx')
    end_path.parent.mkdir(parents=True, exist_ok=True)
    doc_creator.save_document(end_path)
    done_work_text = LocalizationService.BotTexts.DoneWorkText(
        data.get('language', 'ru'))
    await call.message.answer_document(
        FSInputFile(end_path),
        caption=done_work_text,
    )


@gpt_router.callback_query(
    F.data == 'cancel_generation',
    FSMEssayhelper.proceed_action
)
async def cancel_creating(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cancellation_text = LocalizationService.BotTexts.GetCancellationText(
        data.get('language', 'ru'))
    await call.message.answer(
        cancellation_text,
        reply_markup=Keyboard.Get_Back_Button(data.get('language', 'ru'))
    )
