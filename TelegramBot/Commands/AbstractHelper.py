
import asyncio
from Config import dp, bot, gpt_router,router, PATH_TO_TEMP_FILES, GROUP_LINK_URL
from Keyboards.keyboards import Keyboard
from Keyboards import Callbacks
from aiogram import F
from States import  FSMAbstracthelper, FSMUser
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from aiogram.enums.parse_mode import ParseMode
import random
from aiogram import types
from Service import LocalizationService, BotService, AbstractWorkGPTService, GOSTWordDocument, CustomFilters


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'abstract_writer',
    CustomFilters.gptTypeFilter('abstract_writer')
)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    abstract_helper_text = LocalizationService.BotTexts.GetAbstractWelcomeHelperText(
        data.get('language', 'ru'))
    await call.message.edit_text(
        text=abstract_helper_text,
        reply_markup=Keyboard.GenerateWorkButton(
            call.data, data.get('language', 'ru'))
    )
    await state.set_state(FSMAbstracthelper.choosing_action)



@gpt_router.callback_query(
    FSMAbstracthelper.choosing_action,
    F.data == 'abstract_writer',
    CustomFilters.gptTypeFilter('abstract_writer')
)
async def StatWriting(call: types.CallbackQuery, state: FSMContext, ):
    data = await state.get_data()
    abstarct_topic_request_text = LocalizationService.BotTexts.GetAbstractHelperText(
        data.get('language', 'ru'))
    await call.message.answer(
        abstarct_topic_request_text,
    )
    await state.set_state(FSMAbstracthelper.typing_topic)


@gpt_router.message(
    FSMAbstracthelper.typing_topic,
)
async def handleRequestAbstract(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(topic=message.text)
    number_of_pages_text = LocalizationService.BotTexts.SelectNumberOfPages(
        data.get('language', 'ru'))
    await message.answer(
        number_of_pages_text,
        reply_markup=Keyboard.NumberOfPages([10, 13, 15, 18, 20])
    )
    await state.set_state(FSMAbstracthelper.selecting_pages_number)


@gpt_router.callback_query(
    Callbacks.page_number_callback.filter(),
    FSMAbstracthelper.selecting_pages_number
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
    await state.set_state(FSMAbstracthelper.choosing_plan_generation)


@gpt_router.callback_query(
    F.data == 'set_plan',
    FSMAbstracthelper.choosing_plan_generation
)
async def set_plan(call: types.CallbackQuery, state: FSMContext,):
    data = await state.get_data()
    manual_plan = LocalizationService.BotTexts.GetAbstractManualPlan(
        data.get('language','ru'))
    await call.message.edit_text(manual_plan,)
    await state.set_state(FSMAbstracthelper.typing_manual_plan)


@gpt_router.message(
    FSMAbstracthelper.typing_manual_plan
)
async def retrieving_manual_plan(message: types.Message, state: FSMContext,):
    user_text = message.text
    data = await state.get_data()
    thinking_message = await message.answer(LocalizationService.BotTexts.CreatingPlanMessage(data.get('language','ru')))
    abstract_service = data.get('abstract_service')

    if not abstract_service:
        abstract_service = AbstractWorkGPTService(
            external_id=message.from_user.id,
            topic=data['topic'],
            page_number=data['page_number'])
        await state.update_data(abstract_service=abstract_service)
    abstract_service.generate_plan_with_user_detail(user_text)
    plan = await abstract_service.get_plan_response()
    parsed_plan = BotService.parse_work_plan(plan)
    await message.answer(
        LocalizationService.BotTexts.GetPlanScheme(data.get('language','ru')),
    )
    await message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithDonePlan(data.get('language','ru'),),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(FSMAbstracthelper.choosing_action_with_plan)
    await bot.delete_message(chat_id=message.chat.id, message_id=thinking_message.message_id)


@gpt_router.callback_query(
    F.data == 'auto_plan',
    FSMAbstracthelper.choosing_plan_generation
)
async def auto_plan(call: types.CallbackQuery, state: FSMContext,):
    data = await state.get_data()
    thinking_message = await call.message.answer(LocalizationService.BotTexts.CreatingPlanMessage(data.get('language','ru')))
    await bot.send_chat_action(call.message.chat.id, action="typing")

    abstract_service = data.get('abstract_service')

    abstract_service = AbstractWorkGPTService(
        external_id=call.from_user.id,
        topic=data['topic'],
        page_number=data['page_number'])
    await state.update_data(abstract_service=abstract_service)

    abstract_service.get_initial_plan()
    plan = await abstract_service.get_plan_response()
    parsed_plan = BotService.parse_work_plan(plan)
    await call.message.answer(LocalizationService.BotTexts.GetPlanScheme(data.get('language','ru')))

    await call.message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithDonePlan(data.get('language','ru'),),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(FSMAbstracthelper.choosing_action_with_plan)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=thinking_message.message_id)


@gpt_router.callback_query(
    F.data == 'regenerate',
    FSMAbstracthelper.choosing_action_with_plan
)
async def handleRequestAbstract(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    abstract_service: AbstractWorkGPTService = data.get('abstract_service')

    if not abstract_service.is_retries_allowed():
        await call.answer(
            LocalizationService.BotTexts.RegenerationLimitExceded(
                data.get('language','ru')),
            show_alert=True
        )
        return

    await call.message.edit_text(LocalizationService.BotTexts.CreatingPlanMessage(data.get('language','ru')))
    await bot.send_chat_action(call.message.chat.id, action="typing")
    abstract_service.regenerate_plan()
    plan = await abstract_service.get_plan_response()
    parsed_plan = BotService.parse_work_plan(plan)
    await call.message.answer(
        parsed_plan,
        reply_markup=Keyboard.ActionsWithDonePlan(data.get('language','ru')),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(FSMAbstracthelper.choosing_action_with_plan)


@gpt_router.callback_query(
    F.data == 'confirm_plan',
    FSMAbstracthelper.choosing_action_with_plan
)
async def handleRequestAbstract(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    confirm_plan_text = LocalizationService.BotTexts.GetConfirmPlanText(
        data.get('language','ru'))
    await call.message.answer(
        confirm_plan_text,
        reply_markup=Keyboard.GetConfirmationActions(data.get('language','ru'))
    )
    await state.set_state(FSMAbstracthelper.proceed_action)


@gpt_router.callback_query(
    F.data == 'proceed_generation',
    FSMAbstracthelper.proceed_action
)
async def handleRequestAbstract(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    abstract_service: AbstractWorkGPTService = data.get('abstract_service')
    result = await BotService.run_process_with_countdown(
        message=call.message,
        task=abstract_service.build_abstract_work
    )
    doc_creator = GOSTWordDocument(result)
    doc_creator.create_document()
    end_path = PATH_TO_TEMP_FILES.joinpath(str(call.from_user.id)).joinpath(
        f'abstract_{data["topic"][:25]}_{random.randint(1000,2000)}_{call.message.message_id}.docx')
    end_path.parent.mkdir(parents=True, exist_ok=True)
    doc_creator.save_document(end_path)
    done_work_text = LocalizationService.BotTexts.DoneWorkText(
        data.get('language', 'ru'))
    # TODO СБРАСЫВАТЬ ДАННЫЕ ПОСЛЕ КАЖДОЙ ГЕНЕРАЦИИ, ПОТОМУ ЧТО ТАМ БЕРЕТСЯ ИЗ ЛОКАЛ СТОРЕЙДЖА
    await call.message.answer_document(
        FSInputFile(end_path),
        caption=done_work_text,
    )
    await BotService.go_menu(bot=bot,event=call, state=state, final_state=FSMUser.select_mode )


    


@gpt_router.callback_query(
    F.data == 'cancel_generation',
    FSMAbstracthelper.proceed_action
)
async def cancel_creating(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cancellation_text = LocalizationService.BotTexts.GetCancellationText(
        data.get('language','ru'))
    await call.message.answer(
        cancellation_text,
        reply_markup=Keyboard.Get_Back_Button(data.get('language','ru'))
    )
