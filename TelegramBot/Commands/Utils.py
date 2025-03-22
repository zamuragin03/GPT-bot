from Config import dp, bot, router
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram import types
from States import FSMUser
from Keyboards import Keyboard




@router.message(Command('faq'))
async def handlePhoto(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        'https://telegra.ph/FAQ-StudentHelper--GPT-02-15',
        reply_markup=Keyboard.Get_Menu(data.get('language', 'ru'))
    )
    await state.set_state(FSMUser.choosing_action)