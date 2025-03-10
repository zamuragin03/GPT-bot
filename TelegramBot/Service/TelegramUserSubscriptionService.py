from .API import TelegramUserSubscriptionAPI


class TelegramUserSubscriptionService:
    @staticmethod
    def CreateSubscription(external_id, duration):
        res = TelegramUserSubscriptionAPI.CreateUserSubscription(
            external_id=external_id, duration=duration, )
        return res

    @staticmethod
    def GetUserActiveSubscription(external_id):
        subscription_list = TelegramUserSubscriptionAPI.GetUserSubscriptions(
            user__external_id=external_id, is_active=True, ordering="-created_at").get('results')
        if len(subscription_list) == 0:
            return None
        return subscription_list[0]

    @staticmethod
    def IsTrialPeriodOver(external_id):
        subscription_list = TelegramUserSubscriptionAPI.GetUserSubscriptions(
            user__external_id=external_id, is_active=False).get('results')
        return len(subscription_list) > 0

    @staticmethod
    def IsUserNew(external_id):
        sub_count = TelegramUserSubscriptionAPI.GetUserSubscriptions(
            user__external_id=external_id,).get('count')
        return sub_count == 0

    @staticmethod
    def CheckSubscription():
        return TelegramUserSubscriptionAPI.GetDebtUsers()

    @staticmethod
    def GetUserLimitations(external_id):
        return TelegramUserSubscriptionAPI.GetUserLimitations(external_id)
    
    @staticmethod
    def GetUserDailyLimitations(external_id):
        return TelegramUserSubscriptionAPI.GetUserDailyLimitations(external_id)