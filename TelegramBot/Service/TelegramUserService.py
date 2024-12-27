from .API import TGUSerApi


class TelegramUserService():
    @staticmethod
    def CreateTelegramUser(external_id, username, first_name, second_name, ref_external_id):
        
        return TGUSerApi.CreateTelegramUser(external_id, username, first_name, second_name, ref_external_id)


