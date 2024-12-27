
from Config import dp, bot, router, PATH_TO_TEMP_FILES
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMAdmin, FSMAbstracthelper
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.enums.content_type import ContentType
from aiogram import types
from Service import CustomFilters
from Service.BotService import BotService
from Service.GPTService import AbstractWriterGPTService
from Service import GOSTWordDocument


@router.message(
    FSMAbstracthelper.typing_topic,
    CustomFilters.SubscriberUser()
)
async def handleRequestAbstract(message: types.Message, state: FSMContext):
    thinking_message = await message.answer("Генерирую ответ...")
    await bot.send_chat_action(message.chat.id, action="typing")
    topic = message.text
    abstract_gpt = AbstractWriterGPTService(
        topic=topic, external_id=message.from_user.id)
    result = await abstract_gpt.get_abstract()
    doc_creator = GOSTWordDocument(result)
    
    doc_creator.create_document()
    end_path = PATH_TO_TEMP_FILES.joinpath(str(message.from_user.id)).joinpath(
        f'Рефрерат_{topic}_{message.message_id}.docx')
    end_path.parent.mkdir(parents=True, exist_ok=True)
    doc_creator.save_document(end_path)

    await message.answer_document(
        FSInputFile(end_path),
        caption='Ваш готовый реферат:)\nДанная версия не является конечной и требует доработок.\n\n\nНе забудьте добавить титульный лист и оглавление'
    )
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=thinking_message.message_id)
    except:
        pass
