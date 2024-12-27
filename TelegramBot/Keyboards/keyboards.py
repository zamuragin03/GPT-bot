from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters.callback_data import CallbackData
from Service import LocalizationService

KeybardText = LocalizationService.KeyboardTexts


class deposit_callback(CallbackData, prefix="deposit_type"):
    deposit_method: str
    deposit_name: str


class deposit_callback(CallbackData, prefix="deposit_type"):
    deposit_method: str
    deposit_name: str


class get_subscription_callback(CallbackData, prefix="get_subscription"):
    duration: int
    price: float


class Keyboard:
    @staticmethod
    def remove():
        return ReplyKeyboardRemove()

    @staticmethod
    def Get_Menu(selected_language):
        menu = KeybardText.GetMenu()
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=menu[0]['localization'][selected_language]),
                ],
                [
                    KeyboardButton(text=menu[1]['localization'][selected_language]),
                ],
                [
                    KeyboardButton(text=menu[2]['localization'][selected_language]),
                    KeyboardButton(text=menu[3]['localization'][selected_language])
                ],
            ],
            resize_keyboard=True,
        )
        return markup

    @staticmethod
    def Get_Instruments(selected_language):
        all_instruments = KeybardText.GetAllInstruments()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=el['localization'][selected_language], callback_data=el['callback_data']),
            ] for el in all_instruments
        ])
        return markup

    @staticmethod
    def Choose_Language():
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=el['name'], callback_data=el['lang_data'])
            ] for el in KeybardText.GetLanguages()
        ])
        return markup

    @staticmethod
    def Clear_Context_kb(selected_language):
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=KeybardText.GetClearContextText(
                    selected_language), callback_data='clear_context'),
            ],
        ])
        return markup

    @staticmethod
    def Get_Link_To_Channel(selected_language):
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=KeybardText.GetSubscribeButton(selected_language), callback_data='_', url='https://t.me/student_helper_news'),

                ],
                [
                    InlineKeyboardButton(
                        text=KeybardText.DidSubscribeButton(selected_language), callback_data='did_subscribe',),

                ],

            ]
        )
        return markup

    @staticmethod
    def Get_Invitation_Link(selected_language, invitation_link, ):
        back_button = KeybardText.GetBackButton()
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Отправить другу', callback_data='_', url=invitation_link),

                ],
                [
                    InlineKeyboardButton(
                        text=back_button['localization'][selected_language], callback_data=back_button['callback_data'],),

                ],

            ]
        )
        return markup

    @staticmethod
    def Get_Subscription_Keyboard(selected_language):
        menu = list(filter(lambda x: x.get('callback_data') ==
                    'buy_subscription', KeybardText.GetMenu()))
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=el['localization'][selected_language], callback_data=el['callback_data']),
            ] for el in menu
        ])
        return markup

    @staticmethod
    def ActionsWithCourseWorkPlan(selected_language):
        actions = KeybardText.GetActionsWithCoursePlan()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=el['localization'][selected_language], callback_data=el['callback_data']),
            ] for el in actions
        ])
        return markup
