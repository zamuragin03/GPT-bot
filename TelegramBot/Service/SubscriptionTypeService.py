from .API import SubscriptionTypeAPI


class SubscriptionTypeService:
    @staticmethod
    def GetSubscriptionByDuration(duration: int):
        return SubscriptionTypeAPI.GetSubscriptionByDuration(duration)
