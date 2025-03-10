from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Service import LocalizationService

KeybardText = LocalizationService.KeyboardTexts


class KeyboardService:
    def get_menu_option_localization(menu_option: str):
        menu = KeybardText.GetMenu()
        buy_subscription = list(filter(lambda x: x.get('callback_data') == menu_option, menu))[0]
        return buy_subscription.get('localization').values()

    def create_button(el, selected_language, locked=False):
        text = el['localization'][selected_language]
        if locked is None:
            return [InlineKeyboardButton(text=text, callback_data=el['callback_data'])]
        if locked:
            text = "🔒 "+text
        else:
            text = "♾️ "+text
        return [InlineKeyboardButton(text=text, callback_data=el['callback_data'])]

    def check_limits(limitation, helper_type, limits):
        return limitation[helper_type] < limits[helper_type]
