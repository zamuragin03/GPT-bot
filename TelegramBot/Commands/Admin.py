from Config import dp, bot, router
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMAdmin
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile

from aiogram.enums.parse_mode import ParseMode
from aiogram import types
from Service.BotService import BotService
from Service.GPTService import ChatGPTService, PowerPointHelperGPTService




@router.message(Command('test'))
async def handlePhoto(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_state = await state.get_state()
    text_mes ='''• Введение
•• Обоснование выбора темы
•• Объект и предмет исследования
•• Структура работы
• Глава 1: Архитектура и функциональные возможности Nest.js
•• Обзор возможностей Nest.js
•• Архитектурные подходы при разработке с Nest.js
•• Модули и их роль в Nest.js
• Глава 2: Паттерны проектирования для высоконагруженных приложений
•• Использование асинхронного программирования
•• Кэширование и его применение в Nest.js
•• Балансировка нагрузки и распределение задач
• Глава 3: Внедрение и анализ высоконагруженных серверных решений
•• Процесс развертывания приложений
•• Инструменты мониторинга производительности
•• Обеспечение безопасности серверных приложений
• Заключение
•• Основные выводы и результаты
•• Будущие направления исследований
•• Практическая значимость работы
• Список литературы'''
    print(user_data)
    print(user_state)
    await message.answer(text_mes)