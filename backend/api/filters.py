from .models import *
from django_filters import rest_framework as filter


class UserFilter(filter.FilterSet):
    min_balance = filter.NumberFilter(field_name="balance", lookup_expr='gte')
    max_balance = filter.NumberFilter(field_name="balance", lookup_expr='lte')
    max_date = filter.DateFilter(field_name="created_at", lookup_expr='gt')
    min_date = filter.DateFilter(field_name="created_at", lookup_expr='lt')
    class Meta:
        model = TelegramUser
        fields = ('min_balance', 'max_balance', 'created_at', 'referal','max_date', 'min_date')

class UserSubscriptionsFilter(filter.FilterSet):
    class Meta:
        model = UserSubscription
        fields = ('sub_type','user__external_id','created_at','is_active')
