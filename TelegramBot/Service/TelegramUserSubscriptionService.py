from .API import TelegramUserSubscriptionAPI


class TelegramUserSubscriptionService:
    @staticmethod
    def CreateSubscription(external_id, duration):
        return TelegramUserSubscriptionAPI.CreateUserSubscription(external_id=external_id, duration=duration, )

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
    def CheckTrialSubscription():
        return TelegramUserSubscriptionAPI.GetDebtUsers()
