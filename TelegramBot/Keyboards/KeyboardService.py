from Service import LocalizationService

KeybardText = LocalizationService.KeyboardTexts


class KeyboardService:
    def get_menu_option_localization(menu_option: str):
        menu = KeybardText.GetMenu()
        buy_subscription = list(filter(lambda x: x.get('callback_data') == menu_option, menu))[0]
        return buy_subscription.get('localization').values()
