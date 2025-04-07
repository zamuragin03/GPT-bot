from Config import dp, bot, router
from aiogram.utils.deep_linking import decode_payload
from Keyboards import Keyboard, KeyboardService
from aiogram import F
from aiogram.enums.parse_mode import ParseMode

from States import (FSMUser,
                    FSMCodeHelper,
                    FSMChartCreator,
                    FSMPhotoProblem,
                    FSMAbstracthelper,
                    FSMCourseWorkHelper,
                    FSMRewritingHelper,
                    FSMEssayhelper,
                    FSMPPTXHelper,
                    FSMAntiplagitHelper)
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


@router.message(Command('test'))
async def access_admin_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    state = await state.get_state()
    await message.answer(
        '\n'.join([str(data), str(state)]),
        parse_mode=None
    )


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
    thanks_text = LocalizationService.BotTexts.GetThanksForSubscriptionText(
        data.get('language', 'ru'))
    await call.answer(thanks_text, show_alert=True)
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
@router.callback_query(
    F.data == 'back_to_menu',
    FSMPhotoProblem.sending_message
)
@router.callback_query(
    F.data == 'back_to_menu_from_default_mode'
)
async def menu_call(call: types.CallbackQuery, state: FSMContext):

    await BotService.go_menu(bot=bot, event=call, state=state, final_state=FSMUser.select_mode)


@router.message(
    FSMUser.choosing_action,
    F.text.in_(KeyboardService.get_menu_option_localization('instruments'))
)
@router.message(
    F.text.in_(KeyboardService.get_menu_option_localization('instruments'))
)
async def instuments(message: types.Message, state: FSMContext):
    await BotService.go_menu(bot=bot, event=message, state=state, final_state=FSMUser.select_mode)


# Инструменты и коллбэк на inline кнопки

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
    subscription = SubscriptionTypeService.GetSubscriptionByDuration(168)
    subscription_text = BotService.GetSubscriptionPrice(
        data.get('language', 'ru'), subscription)
    await message.answer(
        text=subscription_text,
        parse_mode='HTML',
        reply_markup=Keyboard.GetSubscriptionButton(
            data.get('language', 'ru'), subscription.get('price'))
    )
    await state.set_state(FSMUser.choosing_action_with_sub)


@router.callback_query(
    F.data == 'buy_subscription'
)
async def buy_subscription(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subscription = SubscriptionTypeService.GetSubscriptionByDuration(168)
    subscription_text = BotService.GetSubscriptionPrice(
        data.get('language', 'ru'), subscription)
    await call.message.answer(
        text=subscription_text,
        parse_mode='HTML',
        reply_markup=Keyboard.GetSubscriptionButton(
            data.get('language', 'ru'), subscription.get('price'))
    )
    await state.set_state(FSMUser.choosing_action_with_sub)


@router.callback_query(
    F.data == 'back_to_menu',
    FSMUser.typing_promocode,
)
@router.callback_query(
    F.data == 'back_to_menu',
    FSMUser.in_payment
)
async def buy_subscription(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subscription = SubscriptionTypeService.GetSubscriptionByDuration(168)
    subscription_text = BotService.GetSubscriptionPrice(
        data.get('language', 'ru'), subscription)
    await call.message.edit_text(
        text=subscription_text,
        parse_mode='HTML',
        reply_markup=Keyboard.GetSubscriptionButton(
            data.get('language', 'ru'), subscription.get('price'))
    )
    await state.set_state(FSMUser.choosing_action_with_sub)


@router.callback_query(
    FSMUser.in_fereal_sytem,
)
@router.callback_query(
    F.data == 'back_to_menu',
    FSMUser.choosing_action_with_sub
)
@router.callback_query(
    F.data == 'back_to_menu'
)
@router.callback_query(
    F.data == 'back_to_menu'
)
async def menu(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.answer(
        text='Выберите действие',
        reply_markup=Keyboard.Get_Menu(data.get('language', 'ru'))
    )
    await state.set_state(FSMUser.choosing_action)


@router.callback_query(
    FSMUser.choosing_language,
    F.data.in_(KeyboardService.get_language_codes())
)
async def menu(call: types.CallbackQuery, state: FSMContext):
    human_readable_language = LocalizationService.BotTexts.GetHumanReadableLanguage(
        call.data)
    await call.answer(LocalizationService.BotTexts.GetSelectedLanguage(call.data, human_readable_language), show_alert=True)
    await call.message.delete()
    data = await state.get_data()
    await state.update_data(language=call.data)
    TelegramUserService.SetUserLanguage(call.from_user.id, call.data)
    data = await state.get_data()
    is_new_user = TelegramUserSubscriptionService.IsUserNew(
        call.from_user.id)
    if is_new_user:
        TelegramUserSubscriptionService.CreateSubscription(
            call.from_user.id, 1)
        sub_activated_text = LocalizationService.BotTexts.SubscriptionActivated(
            data.get('language', 'ru'))
        await call.message.answer(
            text=sub_activated_text,
            reply_markup=Keyboard.Get_Menu(data.get('language', 'ru'))
        )
    await call.message.answer(
        text='Выберите действие',
        reply_markup=Keyboard.Get_Menu(data.get('language', 'ru'))
    )
    await state.set_state(FSMUser.choosing_action)


# handle message with chart create


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
        data.get('language', 'ru'))
    invite_link = f"https://t.me/student_helpergpt_bot?start={message.from_user.id}"
    invited_count = TelegramUserService.GetUserReferalsCount(
        message.from_user.id)
    await message.answer(
        text=referal_system_text.format(
            invite_link=invite_link,
            invited_count=invited_count
        ),
        reply_markup=Keyboard.Get_Invitation_Link(
            data.get('language', 'ru'), invite_link),
        parse_mode='HTML'
    )
    await state.set_state(FSMUser.in_fereal_sytem)


@router.callback_query(
    FSMUser.choosing_action_with_sub,
    F.data == 'promocode'
)
async def setup_promocode(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(
        text='Отправьте промокод',
        parse_mode='HTML',
        reply_markup=Keyboard.Get_Back_Button(data.get('language', 'ru'))
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
        status_code, data.get('language', 'ru'))
    await message.answer(
        response_text
    )

    data = await state.get_data()
    await message.answer(
        text='Выберите действие',
        reply_markup=Keyboard.Get_Menu(data.get('language', 'ru'))
    )
    await state.set_state(FSMUser.choosing_action)


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
        message.from_user, user_obj, current_subscription, data.get('language', 'ru'))
    await message.answer(
        text=text_to_send,
        parse_mode='HTML',
        reply_markup=Keyboard.Get_My_Profile_button(data.get('language', 'ru'))
    )
    await state.set_state(FSMUser.choosing_action_with_my_profile)

# смена языка из профиля


@router.callback_query(
    FSMUser.choosing_action_with_my_profile,
    F.data == 'change_language'
)
async def change_language(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete()
    hr_text = LocalizationService.BotTexts.GetHumanReadableLanguage(
        data.get('language', 'ru'))
    await call.message.answer(
        f'Текущий язык: {hr_text} \nВы можете изменить язык',
        reply_markup=Keyboard.Choose_Language()
    )
    await state.set_state(FSMUser.choosing_language)


# Обработка нажатия на помощь
