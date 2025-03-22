from Config import GROUP_LINK_URL, SUBSCRIPTION_LIMITATIONS, DAILY_LIMITATIONS
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from Service import LocalizationService, TelegramUserSubscriptionService
from .Callbacks import Callbacks
from .KeyboardService import KeyboardService
KeybardText = LocalizationService.KeyboardTexts


class Keyboard:
    @staticmethod
    def remove():
        return ReplyKeyboardRemove()

    @staticmethod
    def Get_Admin_Menu():
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text='Статистика'),
                ],
                [
                    KeyboardButton(
                        text='Статистика рефералов'),
                ],
                [
                    KeyboardButton(
                        text='Массовая рассылка'),
                ],

            ], one_time_keyboard=True, resize_keyboard=True
        )
        return markup
    
    @staticmethod
    def GetPeriodTypeKb():
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Все время' ,callback_data='all_time')
            ],
            [
                InlineKeyboardButton(
                    text='В этом месяце' ,callback_data='this_month')
            ],
            [
                InlineKeyboardButton(
                    text='В прошлом месяце' ,callback_data='last_month')
            ],
        ])
        return markup


    @staticmethod
    def GetMassMessageConfirmationKeyboard():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Подтвердить", callback_data="confirm_mass_message"),
                    InlineKeyboardButton(
                        text="Отклонить", callback_data="decline_mass_message"),
                ]
            ]
        )
        return keyboard

    @staticmethod
    def Get_Menu(selected_language):
        menu = KeybardText.GetMenu()
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text=menu[0]['localization'][selected_language]),
                ],
                [
                    KeyboardButton(
                        text=menu[1]['localization'][selected_language]),
                ],
                [
                    KeyboardButton(
                        text=menu[2]['localization'][selected_language]),
                    KeyboardButton(
                        text=menu[3]['localization'][selected_language])
                ],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        return markup

    @staticmethod
    def Get_Instruments(external_id, selected_language):
        all_instruments = KeybardText.GetAllInstruments()
        subscription = TelegramUserSubscriptionService.GetUserActiveSubscription(
            external_id)

        if subscription:
            # Пользователь с активной подпиской
            limitation_object = TelegramUserSubscriptionService.GetUserLimitations(
                external_id)
            limits = SUBSCRIPTION_LIMITATIONS
        else:
            # Пользователь без активной подписки
            limitation_object = TelegramUserSubscriptionService.GetUserDailyLimitations(
                external_id)
            limits = DAILY_LIMITATIONS

        limitation = limitation_object.get('limitations')
        kbs = []

        for el in all_instruments:
            helper_type = el['callback_data']
            try:
                if KeyboardService.check_limits(limitation, helper_type, limits):
                    kbs.append(KeyboardService.create_button(
                        el, selected_language, locked=None))
                else:
                    kbs.append(KeyboardService.create_button(
                        el, selected_language, locked=True))
            except KeyError:
                # Если тип действия отсутствует в лимитах
                kbs.append(KeyboardService.create_button(
                    el, selected_language, locked=None))

        markup = InlineKeyboardMarkup(inline_keyboard=kbs)
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
    def GetPresentationButtons(selected_language):
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=el['localization'][selected_language], callback_data=el['callback_data'])
            ] for el in KeybardText.GetPresentationButtons()
        ])
        return markup

    @staticmethod
    def Pptx_actions_kb(selected_language):
        actions = LocalizationService.KeyboardTexts.GetPresentationOptionsButtons()
        inline_keyboard = [InlineKeyboardButton(
            text=el['localization'][selected_language], callback_data=el['callback_data']) for el in actions]
        markup = InlineKeyboardMarkup(inline_keyboard=[
            inline_keyboard[i:i+2] for i in range(0, len(inline_keyboard), 2)])

        return markup

    @staticmethod
    def Code_helper_buttons(selected_language):
        actions = KeybardText.GetCodeHelperActions()
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=actions[0]['localization'][selected_language], callback_data=actions[0]['callback_data']
                    ),
                    InlineKeyboardButton(
                        text=actions[1]['localization'][selected_language], callback_data=actions[1]['callback_data']
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=actions[2]['localization'][selected_language], callback_data=actions[2]['callback_data']
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=actions[3]['localization'][selected_language], callback_data=actions[3]['callback_data']
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=actions[4]['localization'][selected_language], callback_data=actions[4]['callback_data']
                    ),
                ],

            ]
        )
        return markup

    @staticmethod
    def Get_Link_To_Channel(selected_language):
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=KeybardText.GetSubscribeButton(selected_language), callback_data='_', url=GROUP_LINK_URL),

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
        invitation_button = KeybardText.GetInvitationButton(selected_language)
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=invitation_button.get('text'), switch_inline_query=str(invitation_button.get('switch_inline_query')).format(invitation_link=invitation_link)),
                ],
                [
                    InlineKeyboardButton(
                        text=back_button['localization'][selected_language], callback_data=back_button['callback_data'],),

                ],

            ]
        )
        return markup

    def GetPaymentKeyboard(selected_language, payment_link):
        back_button = KeybardText.GetBackButton()

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=KeybardText.GetPayButtonText(selected_language), url=payment_link),
                ],
                [
                    InlineKeyboardButton(
                        text=back_button['localization'][selected_language], callback_data=back_button['callback_data'],),

                ],

            ]
        )
        return markup

    def GetSubscriptionButton(selected_language, subscription_price):
        sub_button = KeybardText.GetSubscriptionButons()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=str(el['localization'][selected_language]
                             ).format(price=subscription_price),
                    callback_data=el['callback_data']) if el['callback_data'] == 'buy'
                else InlineKeyboardButton(text=el['localization'][selected_language], callback_data=el['callback_data'])
            ] for el in sub_button
        ])
        return markup

    def GetConfirmationActions(selected_language, ):
        buttons = KeybardText.ConfirmationButtonsWithPlan()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=el['localization'][selected_language], callback_data=el['callback_data']),
            ] for el in buttons
        ])
        return markup

    @staticmethod
    def Get_My_Profile_button(selected_language):
        actions = KeybardText.GetMyProfileActions()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=el['localization'][selected_language], callback_data=el['callback_data']),
            ] for el in actions
        ])
        return markup

    @staticmethod
    def Get_Back_Button(selected_language):
        back_button = KeybardText.GetBackButton()
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
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
    def Get_Reasoning_Effort_Kb(selected_language):
        actions = KeybardText.GetReasoningEffortButtons()

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=el['localization'][selected_language],
                                  callback_data=el['callback_data']) for el in actions]])
        return markup

    @staticmethod
    def NumberOfPages(list_of_numbers: list[int]):
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=str(
            el), callback_data=Callbacks.page_number_callback(page_number=int(el)).pack()) for el in list_of_numbers]])
        return markup

    @staticmethod
    def PlanType(selected_language):
        actions = KeybardText.GetPlanActions()

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=el['localization'][selected_language],
                                  callback_data=el['callback_data']) for el in actions]])
        return markup

    @staticmethod
    def ActionsWithDonePlan(selected_language):
        actions = KeybardText.GetActionsWithPlan()

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=el['localization'][selected_language],
                                  callback_data=el['callback_data']) for el in actions]])
        return markup

    @staticmethod
    def ActionsWithPlotCreator(selected_language):
        actions = KeybardText.GetActionsWithChartCreator()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=el['localization'][selected_language], callback_data=el['callback_data']),
            ] for el in actions
        ])
        return markup

    @staticmethod
    def GenerateWorkButton(work_type, selected_language):
        actions = KeybardText.GetGenerateButtons()
        back_button = KeybardText.GetBackButton()

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=actions[work_type]['localization'][selected_language], callback_data=actions[work_type]['callback_data']),
            ],
            [
                InlineKeyboardButton(
                    text=back_button['localization'][selected_language], callback_data=back_button['callback_data'],),

            ],

        ])
        return markup

    @staticmethod
    def GetSlidesCount():
        builder = InlineKeyboardBuilder()

        # Добавляем 25 кнопок с текстом и callback_data
        for i in range(1, 26):
            builder.button(
                text=f"{i}",
                callback_data=f"button_{i}"
            )

        # Группируем кнопки по 5 в ряду
        builder.adjust(5)

        # Возвращаем готовую клавиатуру
        return builder.as_markup()

    @staticmethod
    def GetVerbosityKb(selected_language):
        actions = KeybardText.GetPPTXVerbosity()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=el['localization'][selected_language],
                    callback_data=Callbacks.verbosity_callback(
                        verbosity=str(el['callback_data'])
                    ).pack())
            ] for el in actions
        ])
        return markup

    @staticmethod
    def GetToneKb(selected_language):
        actions = KeybardText.GetPPTXTone()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=el['localization'][selected_language],
                    callback_data=Callbacks.tone_callback(
                        tone=str(el['callback_data'])
                    ).pack())
            ] for el in actions
        ])
        return markup

    @staticmethod
    def GetFetchImagesKb(selected_language):
        actions = KeybardText.GetPPTXFetchMode()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=el['localization'][selected_language],
                    callback_data=Callbacks.fetch_image_callback(
                        fetch_image=str(el['callback_data'])
                    ).pack())
            ] for el in actions
        ])
        return markup
