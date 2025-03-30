from .API import TGUSerApi


class TelegramUserService():
    @staticmethod
    def CreateTelegramUser(external_id, username, first_name, second_name, ref_external_id):
        return TGUSerApi.CreateTelegramUser(external_id, username, first_name, second_name, ref_external_id)

    @staticmethod
    def GetTelegramUserByExternalId(external_id, ):
        return TGUSerApi.GetTelegramUser(external_id,)

    @staticmethod
    def SetUserLanguage(external_id, language):
        return TGUSerApi.UpdateTelegramUser(external_id, language=language)
    
    @staticmethod
    def GetUserReferalsCount(external_id,):
        return TGUSerApi.GetTelegramUsersReferals(external_id).get('referal_count')

    @staticmethod
    def GetAllTelegramUsers():
        return TGUSerApi.GetAllTelegramUsers(page_size=10000).get('results')

    