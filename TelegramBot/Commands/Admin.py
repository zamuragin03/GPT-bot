from Config import dp, bot, admin_router
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMAdmin
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from Service import TelegramUserService, AdminService

from aiogram.enums.parse_mode import ParseMode
from aiogram import types



@admin_router.message(Command('admin_menu'))
async def access_admin_menu(message: types.Message, state: FSMContext):
    await message.answer('Выберите действие админа', reply_markup=Keyboard.Get_Admin_Menu())
    await state.set_state(FSMAdmin.choosing_action)


@admin_router.message(
    FSMAdmin.choosing_action,
    F.text == 'Статистика',
)
async def StatWriting(message: types.Message, state: FSMContext):
    statistic_text = AdminService.GetStatistic()
    await message.answer(statistic_text)

@admin_router.message(
    FSMAdmin.choosing_action,
    F.text == 'Массовая рассылка',
)
async def mass_message(message: types.Message, state: FSMContext):
    await message.answer('Отправьте текст(с фото или без) для рассылки')
    await state.set_state(FSMAdmin.type_mass_message)


@admin_router.message(F.photo, FSMAdmin.type_mass_message)
async def process_mass_message_with_photo(message: types.Message, state: FSMContext):
    caption = message.caption if message.caption else ''
    photo = message.photo[-1].file_id
    
    # Сохраняем фото и текст в состояние FSM
    await state.update_data(mass_message_photo=photo, mass_message_caption=caption)
    
    await message.answer_photo(photo=photo, caption=f"Ваше сообщение:\n\n{caption}", reply_markup=Keyboard.GetMassMessageConfirmationKeyboard())


# Обработка подтверждения рассылки
@admin_router.callback_query(F.data == "confirm_mass_message")
async def confirm_mass_message(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    users = TelegramUserService.GetAllTelegramUsers()
    
    if 'mass_message_text' in data:  # Если это текстовое сообщение
        text = data['mass_message_text']
        for user in users:
            try:
                await bot.send_message(chat_id=user.get('external_id'), text=text, parse_mode=ParseMode.HTML)
            except Exception as e:
                print(f"Failed to send message to {user.get('username')}: {e}")
    
    elif 'mass_message_photo' in data:  # Если это сообщение с фото
        photo = data['mass_message_photo']
        caption = data['mass_message_caption']
        for user in users:
            try:
                await bot.send_photo(chat_id=user.get('external_id'), photo=photo, caption=caption, parse_mode=ParseMode.HTML)
            except Exception as e:
                print(f"Failed to send photo to {user.get('username')}: {e}")
    
    await callback.message.answer('Сообщение отправлено всем пользователям!')
    await state.clear()


@admin_router.callback_query(F.data == "decline_mass_message")
async def decline_mass_message(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Рассылка была отменена.')
    await state.clear()