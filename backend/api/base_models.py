from .serializers import *
from .models import *
from rest_framework.permissions import *

class TelegramUserBaseModel:
    permission_classes = (IsAuthenticated, )
    serializer_class = TelegramUserSerializer
    queryset = TelegramUser.objects.all().order_by('-pk')
    
class UserSubscriptionBaseModel:
    permission_classes = (IsAuthenticated, )
    serializer_class = UserSubscriptionSerializer
    queryset = UserSubscription.objects.all().order_by('-pk')
    
    
class UserActionBaseModel:
    permission_classes = (IsAuthenticated, )
    serializer_class = UserActionsSerializer
    queryset = UserAction.objects.all().order_by('-pk')
    
    