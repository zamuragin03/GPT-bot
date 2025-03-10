from Config import dp, bot, router
from aiogram.utils.deep_linking import decode_payload
from Keyboards import Keyboard, KeyboardService
from aiogram import F
from States import (FSMUser,
                    FSMCodeHelper,
                    FSMChartCreator,
                    FSMPhotoProblem,
                    FSMAbstracthelper,
                    FSMCourseWorkHelper,
                    FSMRewritingHelper,
                    FSMEssayhelper,
                    FSMPPTXHelper)
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from Service import (LocalizationService,
                     CodeHelperGPTService,
                     TelegramUserService,
                     TelegramUserSubscriptionService,
                     BotService,
                     DefaultModeGPTService,
                     RewritingGPTService,
                     SubscriptionTypeService,
                     PromocodeService,
                     CustomFilters)

from aiogram import types


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext, ):
    data = await state.get_data()

    if data.get('language'):
        hr_text = LocalizationService.BotTexts.GetHumanReadableLanguage(
            data.get('language', 'ru')
        )
        await message.answer(
            f'Текущий язык: {hr_text} \nВы можете изменить язык',
            reply_markup=Keyboard.Choose_Language()
        )
    else:
        await message.answer(
            'Выберите язык',
            reply_markup=Keyboard.Choose_Language()
        )
    await state.set_state(FSMUser.choosing_language)


@router.callback_query(
    F.data == 'did_subscribe'
)
async def start(call: types.CallbackQuery, state: FSMContext, ):
    data = await state.get_data()
    if data.get('language'):
        hr_text = LocalizationService.BotTexts.GetHumanReadableLanguage(
            data.get('language', 'ru')
        )
        await call.message.answer(
            f'Текущий язык: {hr_text} \nВы можете изменить язык',
            reply_markup=Keyboard.Choose_Language()
        )
    else:
        choose_language_text = LocalizationService.BotTexts.LanguageRequirementsText()
        await call.message.answer(
            choose_language_text,
            reply_markup=Keyboard.Choose_Language()
        )
    await state.set_state(FSMUser.choosing_language)


@router.callback_query(
    F.data == 'back_to_menu',
    FSMAbstracthelper.choosing_action
)
@router.callback_query(
    F.data == 'back_to_menu',
    FSMPPTXHelper.choosing_action,
)
@router.callback_query(
    F.data == 'back_to_menu',
    FSMCodeHelper.typing_message
)
@router.callback_query(
    F.data == 'back_to_menu',
    FSMEssayhelper.choosing_action
)
@router.callback_query(
    F.data == 'back_to_menu',
    FSMCourseWorkHelper.choosing_action
)
@router.callback_query(
    F.data == 'back_to_menu',
    FSMRewritingHelper.sending_document
)
@router.callback_query(
    F.data == 'back_to_menu',
    FSMChartCreator.choosing_action
)
async def select_language(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(
        text=LocalizationService.BotTexts.GetInstrumentsText(data.get('language', 'ru')),
        reply_markup=Keyboard.Get_Instruments(
            call.from_user.id, data['language'])
    )
    await state.set_state(FSMUser.select_mode)


@router.message(
    FSMUser.choosing_action,
    F.text.in_(KeyboardService.get_menu_option_localization('instruments'))
)
@router.message(
    F.text.in_(KeyboardService.get_menu_option_localization('instruments'))
)
async def instuments(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        text=LocalizationService.BotTexts.GetInstrumentsText(data['language']),
        reply_markup=Keyboard.Get_Instruments(
            message.from_user.id, data['language'])
    )
    await state.set_state(FSMUser.select_mode)
# Инструменты и коллбэк на inline кнопки


@router.callback_query(
    FSMUser.choosing_language,
)
@router.callback_query(
    FSMUser.in_fereal_sytem,
)
@router.callback_query(
    FSMUser.select_mode,
    F.data == 'back_to_menu'
)
@router.callback_query(
    F.data == 'back_to_menu'
)
async def menu(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language_codes = LocalizationService.KeyboardTexts.GetLanguages()
    language_codes = [el.get('lang_data') for el in language_codes]
    # language_codes returns ['ru', 'en',...]
    if data.get('language') is None or call.data in language_codes:
        await state.update_data(language=call.data)
        TelegramUserService.SetUserLanguage(call.from_user.id, call.data)
    data = await state.get_data()
    is_new_user = TelegramUserSubscriptionService.IsUserNew(
        call.from_user.id)
    if is_new_user:
        TelegramUserSubscriptionService.CreateSubscription(
            call.from_user.id, 1)
        sub_activated_text = LocalizationService.BotTexts.SubscriptionActivated(
            data['language'])
        await call.message.answer(
            text=sub_activated_text
        )
    await call.message.answer(
        text='Выберите действие',
        reply_markup=Keyboard.Get_Menu(data['language'])
    )
    await state.set_state(FSMUser.choosing_action)

# handle message with code helper


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'code_helper',
    CustomFilters.gptTypeFilter('code_helper')
)
async def select_language(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Проверка наличия объекта code_helper в состоянии
    code_helper = data.get('code_helper')

    if not code_helper:
        code_helper = CodeHelperGPTService(external_id=call.from_user.id)
        await state.update_data(code_helper=code_helper)
    await call.message.edit_text(
        text=LocalizationService.BotTexts.GetCodeHelperText(data['language']),
        reply_markup=Keyboard.Code_helper_buttons(data['language'])

    )
    await state.set_state(FSMCodeHelper.typing_message)

# handle message with rewriting helper


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'rewriting_helper'
)
async def rewriting_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Проверка наличия объекта code_helper в состоянии
    rewriting_helper = data.get('rewriting_helper')

    if not rewriting_helper:
        rewriting_helper = RewritingGPTService(external_id=call.from_user.id)
        await state.update_data(rewriting_helper=rewriting_helper)
    await call.message.edit_text(
        text=LocalizationService.BotTexts.GetRewritingHelper(data['language']),
        reply_markup=Keyboard.Get_Back_Button(data['language'])
    )
    await state.set_state(FSMRewritingHelper.sending_document)


# handle message with image issue solve
@router.callback_query(
    FSMUser.select_mode,
    F.data == 'photo_issue_helper',
    CustomFilters.gptTypeFilter('photo_issue_helper')
)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text='Отправь фото задачи и я решу ее'
    )
    await state.set_state(FSMPhotoProblem.sending_message)

# handle message with chart create


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'chart_creator_helper',
    CustomFilters.gptTypeFilter('chart_creator_helper')
)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chart_creator_text = LocalizationService.BotTexts.GetChartCreatorInitText(
        data['language'])
    await call.message.edit_text(
        text=chart_creator_text,
        reply_markup=Keyboard.ActionsWithPlotCreator(data['language'])
    )
    await state.set_state(FSMChartCreator.choosing_action)


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'abstract_writer',
    CustomFilters.gptTypeFilter('abstract_writer')
)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    abstract_helper_text = LocalizationService.BotTexts.GetAbstractWelcomeHelperText(
        data.get('language', 'ru'))
    await call.message.edit_text(
        text=abstract_helper_text,
        reply_markup=Keyboard.GenerateWorkButton(
            call.data, data.get('language', 'ru'))
    )
    await state.set_state(FSMAbstracthelper.choosing_action)


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'essay_helper',
    CustomFilters.gptTypeFilter('essay_helper')

)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    abstract_helper_text = LocalizationService.BotTexts.GetEssayWelcomeHelperText(
        data.get('language', 'ru'))
    await call.message.edit_text(
        text=abstract_helper_text,
        reply_markup=Keyboard.GenerateWorkButton(
            call.data, data.get('language', 'ru'))
    )
    await state.set_state(FSMEssayhelper.choosing_action)


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'course_work_helper',
    CustomFilters.gptTypeFilter('course_work_helper')

)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    course_work_text = LocalizationService.BotTexts.GetCourseWorkText(
        data['language'])

    await call.message.edit_text(
        text=course_work_text,
        reply_markup=Keyboard.GenerateWorkButton(
            call.data, data.get('language', 'ru'))
    )
    await state.set_state(FSMCourseWorkHelper.choosing_action)


# Обработка нажатия на реферальную систему
@router.message(
    FSMUser.choosing_action,
    F.text.in_(KeyboardService.get_menu_option_localization('invite_friend'))
)
@router.message(
    F.text.in_(KeyboardService.get_menu_option_localization('invite_friend'))
)
async def invite_friend(message: types.Message, state: FSMContext):
    data = await state.get_data()
    referal_system_text = LocalizationService.BotTexts.ReferalSystemText(
        data['language'])
    invite_link = f"https://t.me/student_helpergpt_bot?start={message.from_user.id}"
    invited_count = TelegramUserService.GetUserReferalsCount(
        message.from_user.id)
    await message.answer(
        text=referal_system_text.format(
            invite_link=invite_link,
            invited_count=invited_count
        ),
        reply_markup=Keyboard.Get_Invitation_Link(
            data['language'], invite_link),
        parse_mode='HTML'
    )
    await state.set_state(FSMUser.in_fereal_sytem)


# Обработка приобретения подписки
@router.message(
    FSMUser.choosing_action,
    F.text.in_(KeyboardService.get_menu_option_localization('buy_subscription'))
)
@router.message(
    F.text.in_(KeyboardService.get_menu_option_localization('buy_subscription'))
)
async def buy_subscription(message: types.Message, state: FSMContext):
    data = await state.get_data()
    subscription_text = LocalizationService.BotTexts.SubscriptionText(
        data['language'])
    subscription = SubscriptionTypeService.GetSubscriptionByDuration(168)
    await message.answer(
        text=subscription_text,
        parse_mode='HTML',
        reply_markup=Keyboard.GetSubscriptionButton(
            data['language'], subscription.get('price'))
    )
    await state.set_state(FSMUser.choosing_action_with_sub)


@router.callback_query(
    FSMUser.choosing_action_with_sub,
    F.data == 'promocode'
)
async def setup_promocode(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.answer(
        text='Отправьте промокод,',
        parse_mode='HTML',
        reply_markup=Keyboard.Get_Back_Button(data['language'])
    )
    await state.set_state(FSMUser.typing_promocode)


# Обработка мой профиль
@router.message(
    FSMUser.typing_promocode,
)
async def my_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()
    status_code = PromocodeService.ActivatePromocode(
        message.from_user.id, message.text)
    response_text = LocalizationService.BotTexts.GetPromocodeText(
        status_code, data['language'])
    await message.answer(
        response_text
    )


# Обработка мой профиль
@router.message(
    FSMUser.choosing_action,
    F.text.in_(KeyboardService.get_menu_option_localization('my_profile'))
)
@router.message(
    F.text.in_(KeyboardService.get_menu_option_localization('my_profile'))
)
async def my_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_subscription = TelegramUserSubscriptionService.GetUserActiveSubscription(
        message.from_user.id)
    user_obj = TelegramUserService.GetTelegramUserByExternalId(
        message.from_user.id)
    text_to_send = BotService.get_my_profile_text(
        message.from_user, user_obj, current_subscription, data['language'])
    await message.answer(
        text=text_to_send,
        parse_mode='HTML',
        reply_markup=Keyboard.Get_My_Profile_button(data['language'])
    )
    await state.set_state(FSMUser.choosing_action_with_my_profile)

# смена языка из профиля


@router.callback_query(
    FSMUser.choosing_action_with_my_profile,
    F.data == 'change_language'
)
async def change_language(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    hr_text = LocalizationService.BotTexts.GetHumanReadableLanguage(
        data['language'])
    await call.message.answer(
        f'Текущий язык: {hr_text} \nВы можете изменить язык',
        reply_markup=Keyboard.Choose_Language()
    )
    await state.set_state(FSMUser.choosing_language)


# Обработка нажатия на помощь


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'default_mode',
    CustomFilters.gptTypeFilter('default_mode')
)
async def default_mode(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    default_mode_helper = data.get('default_mode_helper')
    default_helper_text = LocalizationService.BotTexts.GetDefaultHelperText(
        data['language'])
    if not default_mode_helper:
        default_mode_helper = DefaultModeGPTService(call.from_user.id)
        await state.update_data(default_mode_helper=default_mode_helper)
    await call.message.edit_text(
        text=default_helper_text,
        reply_markup=Keyboard.Code_helper_buttons(data['language']),
        parse_mode='HTML'
    )


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'power_point_helper',
    CustomFilters.gptTypeFilter('power_point_helper')
)
async def select_language(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pptx_text = LocalizationService.BotTexts.GetPPTXWelcomeText(
        data['language'])
    await call.message.edit_text(
        text=pptx_text,
        reply_markup=Keyboard.GetPresentationButtons(data['language'])

    )
    await state.set_state(FSMPPTXHelper.choosing_action)

# handle message with rewriting helper
