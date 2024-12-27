from collections import defaultdict
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from django.shortcuts import render
from .serializers import TelegramUserSerializer, UserActionsSerializer
from rest_framework import generics, status
from .base_models import *
from .filters import *
from .paginators import *
from .models import TelegramUser, UserSubscription, SubscriptionType
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend, NumberFilter


class DeleteTelegramUser(TelegramUserBaseModel, generics.RetrieveDestroyAPIView):
    lookup_field = 'external_id'


class UpdateTelegramUser(TelegramUserBaseModel, generics.RetrieveUpdateAPIView):
    lookup_field = 'external_id'


class GetTelegramUsers(TelegramUserBaseModel, generics.ListAPIView):
    serializer_class = TelegramUserSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    fields = [field.name for field in TelegramUser._meta.get_fields()]
    ordering_fields = '__all__'
    search_fields = ()
    pagination_class = SubscriptionPaginator
    filterset_class = UserFilter


class GetTelegramUser(TelegramUserBaseModel, generics.RetrieveAPIView):
    lookup_field = 'external_id'


class CreateTelegramUser(TelegramUserBaseModel, generics.CreateAPIView):
    def post(self, request, format=None):
        data = request.data.copy()

        referal_external_id = data.pop('ref_external_id', None)

        if referal_external_id:
            try:
                referal = TelegramUser.objects.get(
                    external_id=referal_external_id)
                data['referal'] = referal.id

            except:
                ...
        serializer = TelegramUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CreateUserSubscription(UserSubscriptionBaseModel, generics.CreateAPIView):
    def post(self, request, format=None):
        data = request.data.copy()
        data['is_active'] = True
        subsribe_duration = data.pop('subsribe_duration', None)
        if subsribe_duration:
            try:
                sub_type = SubscriptionType.objects.get(
                    duration=subsribe_duration)
                data['sub_type'] = sub_type.id

            except UserSubscription.DoesNotExist:
                return Response({'error': 'wrong duration'})

        user_external_id = data.pop('user_external_id', None)
        if user_external_id:
            try:
                user = TelegramUser.objects.get(external_id=user_external_id)
                data['user'] = user.id

            except TelegramUser.DoesNotExist:
                return Response({'error': 'wrong external_id'})

        serializer = UserSubscriptionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CreateUserAction(UserActionBaseModel, generics.CreateAPIView):
    def post(self, request, format=None):
        data = request.data.copy()
        model_openai_name = data.pop('model_open_ai_name', None)
        if model_openai_name:
            try:
                model = AIModel.objects.get(open_ai_name=model_openai_name)
                data['model'] = model.id

            except AIModel.DoesNotExist:
                return Response({'error': 'wrong openai name'})

        user_external_id = data.pop('user_external_id', None)
        if user_external_id:
            try:
                user = TelegramUser.objects.get(external_id=user_external_id)
                data['user'] = user.id

            except TelegramUser.DoesNotExist:
                return Response({'error': 'wrong external_id'})

        action_type_name = data.pop('action_type_name', None)
        if action_type_name:
            try:
                action_type = ActionType.objects.get(name=action_type_name)
                data['action_type'] = action_type.id

            except ActionType.DoesNotExist:
                return Response({'error': 'wrong external_id'})

        serializer = UserActionsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class GetUserSubscriptions(UserSubscriptionBaseModel, generics.ListAPIView):
    serializer_class = UserSubscriptionFullSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    fields = [field.name for field in UserSubscription._meta.get_fields()]
    ordering_fields = '__all__'
    # search_fields = ()
    pagination_class = SubscriptionPaginator
    filterset_class = UserSubscriptionsFilter


# exec every 5 minute

class CheckTrialDebtUsers(APIView):
    def post(self, request, format=None):
        expired_users = []
        current_date = timezone.now()
        subscriptions = UserSubscription.objects.filter(
            is_active=True, sub_type__price=0)

        for subscription in subscriptions:
            end_date = subscription.created_at + \
                timezone.timedelta(hours=subscription.sub_type.duration)
            if current_date > end_date:
                subscription.is_active = False
                subscription.save()
                expired_users.append(subscription.user)
        serializer = TelegramUserSerializer(expired_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckWeekDebtUsers(APIView):
    def get(self, request, format=None):
        expired_users = []
        current_date = timezone.now()
        subscriptions = UserSubscription.objects.filter(
            is_active=True, sub_type__price=0)
        for subscription in subscriptions:
            end_date = subscription.created_at + \
                timezone.timedelta(days=subscription.subscription.duration)
            if current_date > end_date:
                subscription.is_active = False
                subscription.save()
                expired_users.append(subscription.user)

        serializer = TelegramUserSerializer(expired_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckUserLimitationsByExternalId(APIView):
    def get(self, request, external_id, format=None):
        # 1. Получаем пользователя по external_id
        try:
            user = TelegramUser.objects.get(external_id=external_id)
        except TelegramUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # 2. Получаем последнюю активную подписку пользователя
        user_subscription = user.usersubscription_set.filter(
            is_active=True).order_by('-created_at').first()

        # Если активной подписки нет, возвращаем объект с нулями для каждого action_type
        if not user_subscription:
            action_counts = {
                action_type.name: None for action_type in ActionType.objects.all()}
            return Response(action_counts, status=200)

        # 3. Вычисляем период действия подписки
        start_time = user_subscription.created_at
        end_time = start_time + \
            timedelta(hours=user_subscription.sub_type.duration)

        # 4. Фильтруем действия пользователя по этому периоду
        user_actions = UserAction.objects.filter(
            user=user,
            created_at__gte=start_time,
            created_at__lte=end_time
        )

        # 5. Создаем словарь, который изначально содержит 0 для всех action_type
        action_counts = {
            action_type.name: 0 for action_type in ActionType.objects.all()}

        # 6. Считаем действия пользователя и обновляем словарь
        for action in user_actions:
            action_counts[action.action_type.name] += 1

        # 7. Возвращаем словарь с подсчетом действий
        return Response(action_counts, status=200)
