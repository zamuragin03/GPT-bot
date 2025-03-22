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
        def GetActionsWithChartCreator():
            return BUTTON_LOCALIZATION_JSON["actions_with_chart_helper"]

        @staticmethod
        def ConfirmationButtonsWithPlan():
            return BUTTON_LOCALIZATION_JSON["confirmation_action_with_done_plan"]

        @staticmethod
        def GetBackButton():
            return list(filter(lambda x: x.get('callback_data') == 'back_to_menu', BUTTON_LOCALIZATION_JSON["instruments"]))[0]

        @staticmethod
        def GetPlanActions():
            return BUTTON_LOCALIZATION_JSON["actions_with_plan"]

        @staticmethod
        def GetCodeHelperActions():
            return BUTTON_LOCALIZATION_JSON["code_helper_actions"]
        
        @staticmethod
        def GetReasoningEffortButtons():
            return BUTTON_LOCALIZATION_JSON["change_reasoning_effort"]

        @staticmethod
        def GetMyProfileActions():
            return BUTTON_LOCALIZATION_JSON["my_profile"]

        @staticmethod
        def GetActionsWithPlan():
            return BUTTON_LOCALIZATION_JSON["actions_with_done_plan"]
        
        @staticmethod
        def GetGenerateButtons() -> str:
            return BUTTON_LOCALIZATION_JSON['generate_buttons']

        @staticmethod
        def GetSubscriptionButons() -> str:
            return BUTTON_LOCALIZATION_JSON['actions_with_subscription']

        @staticmethod
        def GetPresentationButtons() -> str:
            return BUTTON_LOCALIZATION_JSON['pptx_actions']

        @staticmethod
        def GetPresentationOptionsButtons() -> str:
            return BUTTON_LOCALIZATION_JSON['pptx_options']

        @staticmethod
        def GetInvitationButton(selected_language) -> str:
            return BUTTON_LOCALIZATION_JSON['invite_friend_button'][selected_language]

        @staticmethod
        def GetPayButtonText(selected_language) -> str:
            return BUTTON_LOCALIZATION_JSON['pay_button'][selected_language]

        @staticmethod
        def GetPPTXVerbosity() -> str:
            return BUTTON_LOCALIZATION_JSON['choose_verbosity']

        @staticmethod
        def GetPPTXTone() -> str:
            return BUTTON_LOCALIZATION_JSON['choose_tone']

        @staticmethod
        def GetPPTXFetchMode() -> str:
            return BUTTON_LOCALIZATION_JSON['choose_fetch_images']

    class BotTexts:

        @staticmethod
        def GetPPTXToneHR(selected_tone, selected_language) -> str:
            return list(filter(lambda x: x.get('callback_data') == selected_tone, BUTTON_LOCALIZATION_JSON["choose_tone"]))[0].get('localization').get(selected_language)

        @staticmethod
        def GetPPTXVerbosityHR(selected_verbosity, selected_language) -> str:
            return list(filter(lambda x: x.get('callback_data') == selected_verbosity, BUTTON_LOCALIZATION_JSON["choose_verbosity"]))[0].get('localization').get(selected_language)

        @staticmethod
        def GetPPTXFetchImagesHR(selected_fetch_mode, selected_language) -> str:
            return list(filter(lambda x: x.get('callback_data') == selected_fetch_mode, BUTTON_LOCALIZATION_JSON["choose_fetch_images"]))[0].get('localization').get(selected_language)

        @staticmethod
        def GetHumanReadableLanguage(selected_language):
            return list(filter(lambda x: x.get('lang_data') == selected_language, BUTTON_LOCALIZATION_JSON["languages"]))[0].get('name')

        @staticmethod
        def GetStartMessage(selected_language):
            return list(filter(lambda x: x.get('lang_data') == selected_language, BUTTON_LOCALIZATION_JSON["languages"]))[0].get('name')

        @staticmethod
        def GetPlanScheme(selected_language):
            return TEXT_LOCALIZATION_JSON["plan_scheme"][selected_language]

        @staticmethod
        def CreatingPlanMessage(selected_language):
            return TEXT_LOCALIZATION_JSON["creating_plan_message"][selected_language]

        @staticmethod
        def RegenerationLimitExceded(selected_language):
            return TEXT_LOCALIZATION_JSON["plan_regeneration_exceded"][selected_language]

        @staticmethod
        def GenerationTextByWorkType(selected_language, work_type, step):
            return TEXT_LOCALIZATION_JSON["generation_state"][work_type][step][selected_language]

        @staticmethod
        def GetWelcomeMessage(selected_language):
            return TEXT_LOCALIZATION_JSON["start"][selected_language]

        @staticmethod
        def GetInstrumentsText(selected_language):
            return TEXT_LOCALIZATION_JSON["instruments"][selected_language]

        @staticmethod
        def GetCodeHelperText(selected_language):
            return TEXT_LOCALIZATION_JSON["code_helper"][selected_language]

        @staticmethod
        def GetRewritingHelper(selected_language):
            return TEXT_LOCALIZATION_JSON["rewriting_helper"][selected_language]

        @staticmethod
        def GetRewritingDone(selected_language):
            return TEXT_LOCALIZATION_JSON["rewriting_finish"][selected_language]

        @staticmethod
        def GetClearContextText(selected_language):
            return TEXT_LOCALIZATION_JSON["clear_context"][selected_language]
        
        @staticmethod
        def GetReasoningEffortText(selected_language):
            return TEXT_LOCALIZATION_JSON["change_reasoning_effort_text"][selected_language]

        @staticmethod
        def GetSubscriptionRequirements(selected_language):
            return TEXT_LOCALIZATION_JSON["subscription_requirements"][selected_language]

        @staticmethod
        def ReferalSystemText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON["invite_friend_text"][selected_language]

        @staticmethod
        def GetsubscriptionName(name, selected_language) -> str:
            return SUBSCRIPTION_LOCALIZATION_JSON['names'][name][selected_language]

        @staticmethod
        def GetPaymentStatusText(selected_language, is_successfull) -> str:
            return TEXT_LOCALIZATION_JSON['payment_text_status'][str(is_successfull)][selected_language]

        @staticmethod
        def GetPPTXWelcomeText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['pptx_helper_welcome'][selected_language]

        @staticmethod
        def GetPPTXTopicRequest(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['pptx_helper_topic_request'][selected_language]

        @staticmethod
        def GetPPTXSpecificSettingText(setting, selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['pptx_seetings_menu'][setting][selected_language]

        @staticmethod
        def GetPPTXSettings(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['pptx_settings'][selected_language]

        @staticmethod
        def GetNotSpecified(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['not_specified'][selected_language]

        @staticmethod
        def GetMyProfileText(selected_language):
            return TEXT_LOCALIZATION_JSON['profile'][selected_language]

        @staticmethod
        def GetAbstractHelperText(selected_language):
            return TEXT_LOCALIZATION_JSON['abstract_helper'][selected_language]

        @staticmethod
        def GetAbstractManualPlan(selected_language):
            return TEXT_LOCALIZATION_JSON['abstract_manual_plan'][selected_language]

        @staticmethod
        def GetEssayHelperText(selected_language):
            return TEXT_LOCALIZATION_JSON['essay_helper'][selected_language]

        @staticmethod
        def GetConfirmPlanText(selected_language):
            return TEXT_LOCALIZATION_JSON["confirm_plan_action"][selected_language]

        @staticmethod
        def GetCancellationText(selected_language):
            return TEXT_LOCALIZATION_JSON["generation_cancelled"][selected_language]

        @staticmethod
        def GetCancellationText(selected_language):
            return TEXT_LOCALIZATION_JSON["reasonong_effort_changed_succesfully"][selected_language]

        @staticmethod
        def GetCourseWorkWelcomeHelperText(selected_language):
            return TEXT_LOCALIZATION_JSON['course_work_helper_welcome'][selected_language]

        @staticmethod
        def GetEssayWelcomeHelperText(selected_language):
            return TEXT_LOCALIZATION_JSON['essay_helper_welcome'][selected_language]

        @staticmethod
        def GetAbstractWelcomeHelperText(selected_language):
            return TEXT_LOCALIZATION_JSON['abstract_helper_welcome'][selected_language]

        @staticmethod
        def SelectNumberOfPages(selected_language):
            return TEXT_LOCALIZATION_JSON['select_page_number'][selected_language]

        @staticmethod
        def SelectGenerationMode(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['select_generation_mode'][selected_language]

        @staticmethod
        def ChoosePlanType(plan_type, selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['plans'][plan_type][selected_language]
        
        @staticmethod
        def SubscriptionIsOver(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['subscription_over'][selected_language]

        @staticmethod
        def JoinedByInviteLinkText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['join_by_invited_link'][selected_language]

        @staticmethod
        def LanguageRequirementsText() -> str:
            return TEXT_LOCALIZATION_JSON['language_requirements']['ru']

        @staticmethod
        def SubscriptionActivated(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['subscription_activated'][selected_language]

        @staticmethod
        def DoneWorkText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['work_done'][selected_language]

        @staticmethod
        def SubscriptionText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['subscription_description'][selected_language]

        @staticmethod
        def GetCodeHelperAutoSaveText(auto_save_flag, selected_language) -> str:
            return TEXT_LOCALIZATION_JSON[auto_save_flag][selected_language]

        @staticmethod
        def GetUnlimitedTranslation(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON["unlmited_amount"][selected_language]

        @staticmethod
        def GetInactiveSubscriptionText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON["inactive_subscription"][selected_language]

        @staticmethod
        def GetRestrictedText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON["access_resctricted"][selected_language]

        @staticmethod
        def GetLimitiedText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON["subscription_limit_excedeed"][selected_language]
        
        @staticmethod
        def GetDailyLimitiedText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON["daily_limites_excedeed"][selected_language]

        @staticmethod
        def GetPaymentText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON["payment_details"][selected_language]

        @staticmethod
        def GetPromocodeText(status_code, selected_language) -> str:
            return TEXT_LOCALIZATION_JSON["promocode_status"][str(status_code)][selected_language]

        @staticmethod
        def GetCourseWorkText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['course_work_helper'][selected_language]

        @staticmethod
        def GetChartCreatorInitText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['chart_creator_helper'][selected_language]

        @staticmethod
        def GetChartCreatorRulesText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['chart_creator_rules'][selected_language]

        @staticmethod
        def GetChartCreatorDoneGraph(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['chart_creator_done_chart'][selected_language]

        @staticmethod
        def GetDefaultHelperText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['default_mode_helper'][selected_language]

        @staticmethod
        def GetLimitedContextText(selected_language) -> str:
            return TEXT_LOCALIZATION_JSON['context_reached_limit'][selected_language]
