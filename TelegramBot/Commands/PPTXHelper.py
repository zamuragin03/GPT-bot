
from Config import dp, bot, gpt_router, PATH_TO_TEMP_FILES
from Keyboards.keyboards import Keyboard, Callbacks
from aiogram import F
from States import FSMPPTXHelper
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from aiogram.types import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.enums.content_type import ContentType
from aiogram import types
from Service import LocalizationService, BotService, CustomFilters


@gpt_router.callback_query(
    FSMPPTXHelper.choosing_action,
    F.data == 'generate_presentation',
    CustomFilters.gptTypeFilter('power_point_helper')
)
async def StartPPTX(call: types.CallbackQuery, state: FSMContext, ):
    data = await state.get_data()
    await call.message.answer(
        LocalizationService.BotTexts.GetPPTXTopicRequest(data.get('language','ru')),
    )
    await state.set_state(FSMPPTXHelper.typing_topic)


@gpt_router.message(
    FSMPPTXHelper.typing_topic,
)
async def GeneratePPTX(message: types.Message, state: FSMContext):
    await state.update_data(plain_text=message.text)
    data = await state.get_data()
    presentation_settings_text = BotService.GetPPTXSettings(
        selected_language=data.get('language','ru'), **data)
    await message.answer(
        presentation_settings_text,
        reply_markup=Keyboard.Pptx_actions_kb(data.get('language','ru')),
    )
    await state.set_state(FSMPPTXHelper.setting_options)


@gpt_router.callback_query(
    FSMPPTXHelper.setting_options,
    F.data == 'change_verbosity'
)
async def change_verbosity(call: types.CallbackQuery, state: FSMContext, ):
    data = await state.get_data()
    change_verbosity_text = LocalizationService.BotTexts.GetPPTXSpecificSettingText(
        call.data, data.get('language','ru'))
    await call.message.answer(
        text=change_verbosity_text,
        reply_markup=Keyboard.GetVerbosityKb(data.get('language','ru'))
    )

    await state.set_state(FSMPPTXHelper.change_verbosity)

@gpt_router.callback_query(
    Callbacks.verbosity_callback.filter(),
    FSMPPTXHelper.change_verbosity
)
async def changeVerbosity(call: types.CallbackQuery, state: FSMContext, callback_data: Callbacks.verbosity_callback):
    await state.update_data(verbosity=callback_data.verbosity)
    data = await state.get_data()
    presentation_settings_text = BotService.GetPPTXSettings(
        selected_language=data.get('language','ru'), **data)
    await call.message.answer(presentation_settings_text,
                              reply_markup=Keyboard.Pptx_actions_kb(
                                  data.get('language','ru')),
                              )
    await state.set_state(FSMPPTXHelper.setting_options)
    
@gpt_router.callback_query(
    FSMPPTXHelper.setting_options,
    F.data == 'change_language'
)
async def change_language(call: types.CallbackQuery, state: FSMContext, ):
    data = await state.get_data()
    await state.set_state(FSMPPTXHelper.change_language)


@gpt_router.callback_query(
    FSMPPTXHelper.setting_options,
    F.data == 'change_length'
)
async def change_language(call: types.CallbackQuery, state: FSMContext, ):
    data = await state.get_data()
    change_length_text = LocalizationService.BotTexts.GetPPTXSpecificSettingText(
        call.data, data.get('language','ru'))
    await call.message.answer(
        text=change_length_text,
        reply_markup=Keyboard.GetSlidesCount()
    )

    await state.set_state(FSMPPTXHelper.change_length)


# Пример callback_data (уникальный идентификатор кнопки)
@gpt_router.callback_query(
    F.data.startswith("button_"),
    FSMPPTXHelper.change_length
)
async def handle_callback(call: types.CallbackQuery, state: FSMContext,):
    # Здесь F.data фильтрует callback_data, начинающиеся с "button_"
    button_id = call.data.split("_")[1]
    await state.update_data(length=button_id)
    data = await state.get_data()
    presentation_settings_text = BotService.GetPPTXSettings(
        selected_language=data.get('language','ru'), **data)
    await call.message.answer(presentation_settings_text,
                              reply_markup=Keyboard.Pptx_actions_kb(
                                  data.get('language','ru')),
                              )
    await state.set_state(FSMPPTXHelper.setting_options)


@gpt_router.callback_query(
    FSMPPTXHelper.setting_options,
    F.data == 'change_template'
)
async def change_template(call: types.CallbackQuery, state: FSMContext, ):
    data = await state.get_data()

    await state.set_state(FSMPPTXHelper.change_template)


@gpt_router.callback_query(
    FSMPPTXHelper.setting_options,
    F.data == 'change_fetch_images'
)
async def change_fetch_images(call: types.CallbackQuery, state: FSMContext, ):
    data = await state.get_data()
    change_fetch_images_text = LocalizationService.BotTexts.GetPPTXSpecificSettingText(
        call.data, data.get('language','ru'))
    await call.message.answer(
        text=change_fetch_images_text,
        reply_markup=Keyboard.GetFetchImagesKb(data.get('language','ru'))
    )

    await state.set_state(FSMPPTXHelper.change_fetch_images)


@gpt_router.callback_query(
    Callbacks.fetch_image_callback.filter(),
    FSMPPTXHelper.change_fetch_images
)
async def change_image_fetch(call: types.CallbackQuery, state: FSMContext, callback_data: Callbacks.fetch_image_callback):
    await state.update_data(fetch_images=callback_data.fetch_image)
    data = await state.get_data()
    presentation_settings_text = BotService.GetPPTXSettings(
        selected_language=data.get('language','ru'), **data)
    await call.message.answer(presentation_settings_text,
                              reply_markup=Keyboard.Pptx_actions_kb(
                                  data.get('language','ru')),
                              )
    await state.set_state(FSMPPTXHelper.setting_options)
    

@gpt_router.callback_query(
    FSMPPTXHelper.setting_options,
    F.data == 'change_tone'
)
async def change_tone(call: types.CallbackQuery, state: FSMContext, ):
    data = await state.get_data()
    change_tone_text = LocalizationService.BotTexts.GetPPTXSpecificSettingText(
        call.data, data.get('language','ru'))
    await call.message.answer(
        text=change_tone_text,
        reply_markup=Keyboard.GetToneKb(data.get('language','ru'))
    )
    await state.set_state(FSMPPTXHelper.change_tone)

@gpt_router.callback_query(
    Callbacks.tone_callback.filter(),
    FSMPPTXHelper.change_tone
)
async def changeTone(call: types.CallbackQuery, state: FSMContext, callback_data: Callbacks.tone_callback):
    await state.update_data(tone=callback_data.tone)
    data = await state.get_data()
    presentation_settings_text = BotService.GetPPTXSettings(
        selected_language=data.get('language','ru'), **data)
    await call.message.answer(presentation_settings_text,
                              reply_markup=Keyboard.Pptx_actions_kb(
                                  data.get('language','ru')),
                              )
    await state.set_state(FSMPPTXHelper.setting_options)