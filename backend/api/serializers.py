
from api.models import *
from rest_framework import serializers


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = '__all__'


class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = '__all__'
        
class UserActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = '__all__'


class SubscriptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = '__all__'


class UserSubscriptionFullSerializer(serializers.ModelSerializer):
    sub_type = SubscriptionTypeSerializer()
    user = TelegramUserSerializer()

    class Meta:
        model = UserSubscription
        fields = '__all__'