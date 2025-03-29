import asyncio
from Config import dp, bot, admin_router
from Keyboards.keyboards import Keyboard
from aiogram import F
from States import FSMAdmin, FSMUser
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from Service import TelegramUserService, AdminService, BotService

from aiogram.enums.parse_mode import ParseMode
from aiogram import types
    
@admin_router.message(Command('admin_menu'))
async def access_admin_menu(message: types.Message, state: FSMContext):
    await message.answer('Выберите действие админа', reply_markup=Keyboard.Get_Admin_Menu())
    await state.set_state(FSMAdmin.choosing_action)


@admin_router.message(
    F.text == '⬅️Назад⬅️',
    FSMAdmin.choosing_action
)
async def Back_to_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        text='Выберите действие',
        reply_markup=Keyboard.Get_Menu(data.get('language', 'ru'))
    )
    await state.set_state(FSMUser.choosing_action)
    
@admin_router.message(
    FSMAdmin.choosing_action,
    F.text == 'Статистика',
)
async def StatWriting(message: types.Message, state: FSMContext):
    statistic_text = AdminService.GetStatistic()
    await message.answer(statistic_text)


@admin_router.message(
    FSMAdmin.choosing_action,
    F.text == 'Статистика рефералов',
)
async def StatWriting(message: types.Message, state: FSMContext):
    await message.answer('Выберите период', reply_markup=Keyboard.GetPeriodTypeKb())


@admin_router.callback_query(
    F.data=='back_to_menu',
    FSMAdmin.choosing_action
)
async def back_to_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Выберите действие админа', reply_markup=Keyboard.Get_Admin_Menu())
    await state.set_state(FSMAdmin.choosing_action)

@admin_router.callback_query(
    F.data.in_({'last_month', 'this_month', 'all_time'})
)
async def get_stat(call: types.CallbackQuery, state: FSMContext):
    result = AdminService.GetReferalStat(call.data)
    format_text = BotService.formatReferals(result, call.data)
    await call.message.edit_text(
        format_text,
        reply_markup=Keyboard.GetPeriodTypeKb()
    )


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
    await state.update_data(mass_message_type='photo', mass_message_caption=caption, mass_message_photo=photo)

    await message.answer_photo(photo=photo, caption=f"Ваше сообщение:\n\n{caption}", reply_markup=Keyboard.GetMassMessageConfirmationKeyboard())


@admin_router.message(F.text, FSMAdmin.type_mass_message)
async def process_mass_message_with_text(message: types.Message, state: FSMContext):

    await state.update_data(mass_message_type='text', mass_message_caption=message.text)

    await message.answer(text=f"Ваше сообщение:\n\n{message.text}", reply_markup=Keyboard.GetMassMessageConfirmationKeyboard())


# Обработка подтверждения рассылки
@admin_router.callback_query(F.data == "confirm_mass_message")
async def confirm_mass_message(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    users = TelegramUserService.GetAllTelegramUsers()
    message_type = data['mass_message_type']
    text = data['mass_message_caption']
    if message_type == 'text':
        for user in users:
            try:
                await bot.send_message(chat_id=user.get('external_id'), text=text, parse_mode=ParseMode.HTML)
            except Exception as e:
                print(f"Failed to send message to {user.get('username')}: {e}")

    if message_type == 'photo':
        for user in users:
            try:
                await bot.send_photo(chat_id=user.get('external_id'), photo=data['mass_message_photo'], caption=text, parse_mode=ParseMode.HTML)
            except Exception as e:
                print(f"Failed to send photo to {user.get('username')}: {e}")

    await callback.message.answer('Сообщение отправлено всем пользователям!')
    await state.clear()


@admin_router.callback_query(F.data == "decline_mass_message")
async def decline_mass_message(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Рассылка была отменена.')
    await callback.message.answer('Выберите действие админа', reply_markup=Keyboard.Get_Admin_Menu())
    await state.set_state(FSMAdmin.choosing_action)
