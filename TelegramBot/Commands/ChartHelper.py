
import asyncio
from Config import dp, bot, router,gpt_router, GROUP_LINK_URL
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMAdmin, FSMChartCreator, FSMUser
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.enums.content_type import ContentType
from aiogram import types
from Service import CustomFilters, BotService, ChartCreatorGPTService, LocalizationService


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'chart_creator_helper',
    CustomFilters.gptTypeFilter('chart_creator_helper')
)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chart_creator_text = LocalizationService.BotTexts.GetChartCreatorInitText(
        data.get('language', 'ru'))
    await call.message.edit_text(
        text=chart_creator_text,
        reply_markup=Keyboard.ActionsWithPlotCreator(
            data.get('language', 'ru'))
    )
    await state.set_state(FSMChartCreator.choosing_action)



@gpt_router.callback_query(
    F.data == 'plot_graph',
    FSMChartCreator.choosing_action,
    CustomFilters.gptTypeFilter('chart_creator_helper')

)
async def handleRequest(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    rules_text = LocalizationService.BotTexts.GetChartCreatorRulesText(
        data.get('language','ru'))
    await call.message.answer(rules_text),
    await state.set_state(FSMChartCreator.typing_request)


@gpt_router.message(
    FSMChartCreator.typing_request,
)
async def handleRequest(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chart_creator = ChartCreatorGPTService(message.from_user.id)
    chart_creator.add_message(message.text)
    
    result = await BotService.run_process_with_countdown(
        message=message,
        task=chart_creator.GetChartCode   # Задача
    )
    if result.leave:
        await message.answer('incorrect query')
    else:
        try:
            done_chart_text = LocalizationService.BotTexts.GetChartCreatorDoneGraph(
                data.get('language','ru'))
            image_to_send = BotService.create_image_by_user_requset(
                result, message.from_user.id)
            await message.answer_photo(
                caption=done_chart_text,
                photo=image_to_send,
            )
        except Exception as e:
            print(e)
            await message.answer('Too complicated for me')
        finally:
            await message.answer(
                text='Выберите действие',
                reply_markup=Keyboard.Get_Menu(data.get('language', 'ru'))
            )
            await state.set_state(FSMUser.choosing_action)