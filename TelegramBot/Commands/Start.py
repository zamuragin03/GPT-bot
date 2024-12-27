from Config import dp, bot, router
from aiogram.utils.deep_linking import decode_payload
from Keyboards import Keyboard, KeyboardService
from aiogram import F
from States import FSMUser, FSMCodeHelper, FSMChartCreator,  FSMPhotoProblem, FSMAbstracthelper,FSMCourseWorkHelper
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from Service import LocalizationService, CodeHelperGPTService, TelegramUserService, TelegramUserSubscriptionService, BotService, DefaultModeGPTService

from aiogram import types

BotTexts = LocalizationService.BotTexts


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext, ):
    data = await state.get_data()
    if data.get('language'):
        hr_text = BotTexts.GetHumanReadableLanguage(data['language'])
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
async def did_subscribe(call: types.CallbackQuery, state: FSMContext, ):
    if not await BotService.check_user_subscription(call):
        return
    data = await state.get_data()
    subscription_object = TelegramUserSubscriptionService.GetUserActiveSubscription(
        call.from_user.id)
    print(subscription_object)
    is_trial_over = TelegramUserSubscriptionService.IsTrialPeriodOver(
        call.from_user.id)
    print(is_trial_over)
    if is_trial_over:
        await call.message.answer(
            'Ваша действующая подписка закончилась. Давайте возьмем новую?',
            reply_markup=Keyboard.Get_Menu('ru')

            # reply_markup=Keyboard.
        )
        return
    if subscription_object is None:
        TelegramUserSubscriptionService.CreateSubscription(
            call.from_user.id, duration=1)
        await call.message.answer(
            'Активировали для вас пробную подписку на 1 час.\nВозможности бота',
            reply_markup=Keyboard.Get_Menu('ru')

        )


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
async def menu(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data.get('language') is None or call.data in ['ru', 'en']:
        await state.update_data(language=call.data)
    data = await state.get_data()
    welcome_message = BotTexts.GetWelcomeMessage(
        call.from_user.id, data['language'])
    await call.message.answer(
        text=welcome_message,
        reply_markup=Keyboard.Get_Menu(data['language'])
    )
    await state.set_state(FSMUser.choosing_action)


@router.message(
    FSMUser.choosing_action,
    F.text.in_(KeyboardService.get_menu_option_localization('instruments'))
)
@router.message(
    F.text.in_(KeyboardService.get_menu_option_localization('instruments'))
)
async def select_language(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        text=BotTexts.GetInstrumentsText(data['language']),
        reply_markup=Keyboard.Get_Instruments(data['language'])
    )
    await state.set_state(FSMUser.select_mode)


# handle message with code helper
@router.callback_query(
    FSMUser.select_mode,
    F.data == 'code_helper'
)
async def select_language(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Проверка наличия объекта code_helper в состоянии
    code_helper = data.get('code_helper')

    if not code_helper:
        code_helper = CodeHelperGPTService(external_id=call.from_user.id)
        await state.update_data(code_helper=code_helper)
    await call.message.edit_text(
        text=BotTexts.GetCodeHelperText(data['language']),

    )
    await state.set_state(FSMCodeHelper.typing_message)


# handle message with image issue solve
@router.callback_query(
    FSMUser.select_mode,
    F.data == 'photo_issue_helper'
)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text='Отправь фото задачи и я решу ее'
    )
    await state.set_state(FSMPhotoProblem.sending_message)

# handle message with chart create


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'chart_creator_helper'
)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text='Напиши какой график построить и я отправлю его тебе(можно указать границы значений по x[x from -1 to 1])'
    )
    await state.set_state(FSMChartCreator.typing_request)


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'abstract_writer'
)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text='Вас приветствует мастер по написани Рефератов/эссе. Давай решим какая будет тема '
    )
    await state.set_state(FSMAbstracthelper.typing_topic)

@router.callback_query(
    FSMUser.select_mode,
    F.data == 'course_work_helper'
)
async def chart_creator_helper(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text='Вас приветствует мастер по написани Курсовых работ. Давай решим какая будет тема '
    )
    await state.set_state(FSMCourseWorkHelper.typing_topic)


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
    referal_system_text = BotTexts.ReferalSystemText(data['language'])
    invite_link = f"https://t.me/student_helpergpt_bot?start={message.from_user.id}"
    await message.answer(
        text=referal_system_text.format(
            invite_link=invite_link, invited_count=10),
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
    await message.answer(
        text='Тут описывается процесс покупки подписки, преимущества и тд',
        parse_mode='HTML'
    )

# Обработка мой профиль


@router.message(
    FSMUser.choosing_action,
    F.text.in_(KeyboardService.get_menu_option_localization('my_profile'))
)
@router.message(
    F.text.in_(KeyboardService.get_menu_option_localization('my_profile'))
)
async def buy_subscription(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_subscription = TelegramUserSubscriptionService.GetUserActiveSubscription(
        message.from_user.id)
    text_to_send = BotService.get_my_profile_text(
        message.from_user, current_subscription, data['language'])
    await message.answer(
        text=text_to_send,
        parse_mode='HTML',
        reply_markup=Keyboard.Get_Menu(data['language'])
    )

# Обработка нажатия на помощь

# Обработка нажатия на мой профиль


@router.callback_query(
    FSMUser.select_mode,
    F.data == 'default_mode'
)
async def default_mode(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Проверка наличия объекта code_helper в состоянии
    default_mode_helper = data.get('default_mode_helper')

    if not default_mode_helper:
        default_mode_helper = DefaultModeGPTService(call.from_user.id)
        await state.update_data(default_mode_helper=default_mode_helper)
    await call.message.edit_text(
        text='Добро пожаловать в свободный режим. Отправляйте любое сообщение(в том числе с фото)',
        parse_mode='HTML'
    )
