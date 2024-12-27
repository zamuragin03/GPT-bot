
from Config import dp, bot, router
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMAdmin, FSMChartCreator
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.enums.content_type import ContentType
from aiogram import types
from Service import CustomFilters
from Service.BotService import BotService
from Service.GPTService import ChatGPTService, PowerPointHelperGPTService, ChartCreatorGPTService


@router.message(
    FSMChartCreator.typing_request,
    CustomFilters.SubscriberUser()
)
async def handleRequest(message: types.Message, state: FSMContext):
    
    chart_creator = ChartCreatorGPTService(message.from_user.id)
    response_from_chat = await chart_creator.GetChartCode(message.text)
    if response_from_chat.leave:
        await message.answer('Не надо вводить в запросы для графиков всякую фигню)')
    else:
        try:
            image_to_send = BotService.create_image_by_user_requset(
                response_from_chat, message.from_user.id)
            await message.answer_photo(
                caption=response_from_chat.title,
                photo=image_to_send,
            )
        except Exception as e:
            print(e)
            await message.answer('Извините, но такой график я построить не смогу')

