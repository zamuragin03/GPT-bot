
import asyncio
from Config import dp, bot, gpt_router, GROUP_LINK_URL
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMAdmin, FSMChartCreator
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.enums.content_type import ContentType
from aiogram import types
from Service import CustomFilters, BotService, ChartCreatorGPTService, LocalizationService


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
    typing_text = LocalizationService.BotTexts.GenerationTextByWorkType(
        data.get('language','ru'), 'chart', 'start')
    demand_minutes, demand_seconds = 0, 15
    finish_text = LocalizationService.BotTexts.GenerationTextByWorkType(
        data.get('language','ru'), 'chart', 'finish')
    countdown_message = await message.answer(typing_text.format(
        minutes=demand_minutes,
        seconds=demand_seconds,
        url=GROUP_LINK_URL,
    ), parse_mode=ParseMode.HTML)
    countdown_task = asyncio.create_task(
        BotService.countdown(call=None,
                             countdown_message=countdown_message,
                             duration=demand_minutes*60+demand_seconds,
                             interval=1,
                             new_text=typing_text,
                             finish_text=finish_text)
    )
    response_from_chat = await chart_creator.GetChartCode(message.text)

    if response_from_chat.leave:
        await message.answer('error')
    else:
        try:
            done_chart_text = LocalizationService.BotTexts.GetChartCreatorDoneGraph(
                data.get('language','ru'))
            image_to_send = BotService.create_image_by_user_requset(
                response_from_chat, message.from_user.id)
            await message.answer_photo(
                caption=done_chart_text,
                photo=image_to_send,
            )
        except Exception as e:
            print(e)
            await message.answer('Too complicated for me')

    countdown_task.cancel()
    try:
        await countdown_message.delete()
    except Exception as e:
        pass
