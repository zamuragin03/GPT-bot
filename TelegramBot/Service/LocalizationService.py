from Config import TEXT_LOCALIZATION_JSON, BUTTON_LOCALIZATION_JSON, SUBSCRIPTION_LOCALIZATION_JSON


class LocalizationService:
    class KeyboardTexts:

        @staticmethod
        def GetAllInstruments():
            return BUTTON_LOCALIZATION_JSON["instruments"]

        @staticmethod
        def GetClearContextText(selected_language):
            return BUTTON_LOCALIZATION_JSON["clear_context"][selected_language]

        @staticmethod
        def GetSubscribeButton(selected_language):
            return BUTTON_LOCALIZATION_JSON["link_to_channel"][selected_language]

        @staticmethod
        def DidSubscribeButton(selected_language):
            return BUTTON_LOCALIZATION_JSON["did_subscribe"][selected_language]

        @staticmethod
        def GetMenu():
            return BUTTON_LOCALIZATION_JSON["menu"]

        @staticmethod
        def GetLanguages():
            return BUTTON_LOCALIZATION_JSON["languages"]

        @staticmethod
        def GetActionsWithCoursePlan():
            return BUTTON_LOCALIZATION_JSON["actions_with_course_work_plan"]

        @staticmethod
        def GetBackButton():
            return list(filter(lambda x: x.get('callback_data') == 'back_to_menu', BUTTON_LOCALIZATION_JSON["instruments"]))[0]

    class BotTexts:

        @staticmethod
        def GetHumanReadableLanguage(selected_language):
            return list(filter(lambda x: x.get('lang_data') == selected_language, BUTTON_LOCALIZATION_JSON["languages"]))[0].get('name')

        @staticmethod
        def GetWelcomeMessage(external_id, selected_language):
            return TEXT_LOCALIZATION_JSON["welcome"]["1_hour_free"][selected_language]

        @staticmethod
        def GetInstrumentsText(selected_language):
            return TEXT_LOCALIZATION_JSON["instruments"][selected_language]

        @staticmethod
        def GetCodeHelperText(selected_language):
            return TEXT_LOCALIZATION_JSON["code_helper"][selected_language]

        @staticmethod
        def GetClearContextText(selected_language):
            return TEXT_LOCALIZATION_JSON["code_helper_clear_context"][selected_language]

        @staticmethod
        def GetSubscriptionRequirements(selected_language):
            return TEXT_LOCALIZATION_JSON["subscription_requirements"][selected_language]

        @staticmethod
        def ReferalSystemText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON["invite_friend_text"][selected_language]

        @staticmethod
        def GetsubscriptionName(period, selected_language) -> str:
            return SUBSCRIPTION_LOCALIZATION_JSON['names'][period][selected_language]

        @staticmethod
        def GetMyProfileText(selected_language):
            return TEXT_LOCALIZATION_JSON['profile'][selected_language]

    
