from .serializers import *
from .models import *
from rest_framework.permissions import *

class AdminTelegramUserBaseModel:
    permission_classes = (IsAuthenticated, )
    serializer_class = AdminTelegramUserSerializer
    queryset = AdminTelegramUser.objects.all().order_by('-pk')
    
class TelegramUserBaseModel:
    permission_classes = (IsAuthenticated, )
    serializer_class = TelegramUserSerializer
    queryset = TelegramUser.objects.all().order_by('-pk')
    
class UserSubscriptionBaseModel:
    permission_classes = (IsAuthenticated, )
    serializer_class = UserSubscriptionSerializer
    queryset = UserSubscription.objects.all().order_by('-pk')

class SubscriptionBaseModel:
    permission_classes = (IsAuthenticated, )
    serializer_class = SubscriptionTypeSerializer
    queryset = SubscriptionType.objects.all().order_by('-pk')

class UserActionBaseModel:
    permission_classes = (IsAuthenticated, )
    serializer_class = UserActionsSerializer
    queryset = UserAction.objects.all().order_by('-pk')
    
class PaymentBaseModel:
    permission_classes = (IsAuthenticated, )
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all().order_by('-pk')
    