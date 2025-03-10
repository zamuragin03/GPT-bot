from Config import dp, bot, router
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram import types




@router.message(Command('faq'))
async def handlePhoto(message: types.Message, state: FSMContext):
    await message.answer(
        'https://telegra.ph/FAQ-StudentHelper--GPT-02-15'
    )