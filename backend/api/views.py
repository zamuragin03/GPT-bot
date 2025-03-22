from collections import defaultdict
from datetime import timedelta
from django.utils import timezone
from .Services import create_or_extend_subscription, StatisticService
from rest_framework.views import APIView
from django.http import JsonResponse
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
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .DTOs import PromocodeDTO
from rest_framework.permissions import IsAuthenticated


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


class GetAdminTelegramUsers(AdminTelegramUserBaseModel, generics.ListAPIView):
    serializer_class = AdminTelegramUserSerializer


class GetTelegramUser(TelegramUserBaseModel, generics.RetrieveAPIView):
    lookup_field = 'external_id'


class GetSubscription(SubscriptionBaseModel, generics.RetrieveAPIView):
    lookup_field = 'duration'


class CreatePayment(PaymentBaseModel, generics.CreateAPIView):
    def post(self, request, format=None):
        print(request.data)
        data = request.data.copy()

        external_id = data.pop('external_id', None)

        if external_id:
            try:
                user = TelegramUser.objects.get(
                    external_id=external_id)
                data['user'] = user.id

            except:
                ...
        serializer = PaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UpdatePayment(PaymentBaseModel, generics.RetrieveUpdateAPIView):
    lookup_field = 'order_id'

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetPayment(PaymentBaseModel, generics.RetrieveAPIView):
    lookup_field = 'order_id'


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
        subscribe_duration = data.pop('subscribe_duration', None)
        if subscribe_duration:
            try:
                sub_type = SubscriptionType.objects.get(
                    duration=subscribe_duration)
                data['sub_type'] = sub_type.id
            except SubscriptionType.DoesNotExist:
                return Response({'error': 'wrong duration'}, status=status.HTTP_400_BAD_REQUEST)

        user_external_id = data.pop('user_external_id', None)
        if user_external_id:
            try:
                user = TelegramUser.objects.get(external_id=user_external_id)
                data['user'] = user.id
                response_data = create_or_extend_subscription(user, sub_type)
                return Response(response_data)
            except TelegramUser.DoesNotExist:
                return Response({'error': 'wrong external_id'}, status=status.HTTP_400_BAD_REQUEST)

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


class ActivatePromocodeView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = PromocodeDTO(data=request.data)
        if serializer.is_valid():
            external_id = serializer.validated_data['external_id']
            promocode_text = serializer.validated_data['promocode_text']

            # Ищем промокод в БД
            try:
                promocode = UserPromocode.objects.get(
                    promocode_text=promocode_text, is_active=True)
            except UserPromocode.DoesNotExist:
                return Response({'error': 'Promocode does not exist or is not active.'}, status=status.HTTP_400_BAD_REQUEST)

            # Получаем пользователя по external_id
            user = get_object_or_404(TelegramUser, external_id=external_id)

            # Используем общую функцию для создания или продления подписки
            response_data = create_or_extend_subscription(
                user, promocode.sub_type)

            # Деактивируем промокод
            promocode.is_active = False
            promocode.save()

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# exec every 5 minute

class CheckDebtUsers(APIView):
    def post(self, request, format=None):
        expired_users = []
        current_date = timezone.now()
        subscriptions = UserSubscription.objects.filter(
            is_active=True, sub_type__duration__lt=1000)
        for subscription in subscriptions:
            if current_date > subscription.till:
                subscription.is_active = False
                subscription.save()
                expired_users.append(subscription)
        serializer = UserSubscriptionFullSerializer(expired_users, many=True)
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
            return Response({}, status=404)

        # 2. Получаем последнюю активную подписку пользователя
        user_subscription = user.usersubscription_set.filter(
            is_active=True).order_by('-created_at').first()
        # Если активной подписки нет, возвращаем объект с нулями для каждого action_type
        if not user_subscription:
            action_counts = {
                action_type.name: 0 for action_type in ActionType.objects.all()}
            response_data = {
                "user": TelegramUserSerializer(user).data,
                "limitations": action_counts
            }
            return Response(response_data, status=200)

        # 3. Вычисляем период действия подписки
        start_time = user_subscription.created_at
        end_time = user_subscription.till
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
        response_data = {
            "user": TelegramUserSerializer(user).data,
            "limitations": action_counts
        }
        return Response(response_data, status=200)


class CheckUserActionsLast24Hours(APIView):
    def get(self, request, external_id, format=None):
        # 1. Получаем пользователя по external_id
        try:
            user = TelegramUser.objects.get(external_id=external_id)
        except TelegramUser.DoesNotExist:
            return Response({}, status=404)

        # 2. Вычисляем время 24 часа назад
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=24)

        # 3. Фильтруем действия пользователя за последние сутки
        user_actions = UserAction.objects.filter(
            user=user,
            created_at__gte=start_time,
            created_at__lte=end_time
        )
        # 4. Создаем словарь, который изначально содержит 0 для всех action_type
        action_counts = {
            action_type.name: 0 for action_type in ActionType.objects.all()
        }

        # 5. Считаем действия пользователя и обновляем словарь
        for action in user_actions:
            action_counts[action.action_type.name] += 1

        # 6. Возвращаем словарь с подсчетом действий
        response_data = {
            "user": TelegramUserSerializer(user).data,
            "limitations": action_counts
        }
        return Response(response_data, status=200)


class CheckReferals(APIView):
    def get(self, request, external_id, format=None):
        try:
            user = TelegramUser.objects.get(external_id=external_id)
            referal_count = TelegramUser.objects.filter(referal=user).count()
            return Response({"referal_count": referal_count}, status=status.HTTP_200_OK)
        except TelegramUser.DoesNotExist:
            return Response({"referal_count": 0}, status=status.HTTP_200_OK)


class TopReferralsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Получаем query-параметр
        referral_type = request.query_params.get('type', None)

        # Проверяем параметр и вызываем соответствующую функцию
        if referral_type == "all_time":
            data = StatisticService.get_top_referrals_all_time()
            return Response(data)
        elif referral_type == "this_month":
            data = StatisticService.get_top_referrals_this_month()
            return Response(data)
        elif referral_type == "last_month":
            data = StatisticService.get_top_referrals_last_month()
            return Response( data)
        else:
            return Response({"error": "Invalid type parameter. Use 'all_time', 'this_month', or 'last_month'."}, status=400)


class StatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        statistics = {
            "total_users": StatisticService.get_total_users(),
            "unbanned_users": StatisticService.get_unbanned_users(),
            "registered_today": StatisticService.get_registered_today_count(),
            "new_users_current_month": StatisticService.get_new_users_current_month(),
            "new_users_last_month": StatisticService.get_new_users_last_month(),
            "current_month_subscribers": StatisticService.current_month_subscribers_count(),
            "last_month_subscribers": StatisticService.last_month_subscribers_count(),
            "today_subscribers": StatisticService.today_subscribers_count(),
            "today_subscribers_bought": StatisticService.today_subscribers_bought_count(),
            "this_month_subscribers_bought": StatisticService.this_month_subscribers_bought_count(),
            "last_month_subscribers_bought": StatisticService.last_month_subscribers_bought_count(),
            "active_subscribers": StatisticService.get_active_subscribers_count(),
            "admins_count": StatisticService.get_admins_count(),
            "requests_today": StatisticService.get_requests_today(),
            "requests_yesterday": StatisticService.get_requests_yesterday(),
            "requests_current_month": StatisticService.get_requests_current_month(),
            "tokens_spent_today": StatisticService.get_tokens_spent_today(),
            "tokens_spent_yesterday": StatisticService.get_tokens_spent_yesterday(),
            "tokens_spent_current_month": StatisticService.get_tokens_spent_current_month(),
            "tokens_spent_last_month": StatisticService.get_tokens_spent_last_month(),
            "income_today": StatisticService.get_income_today(),
            "income_yesterday": StatisticService.get_income_yesterday(),
            "last_month_revenue": StatisticService.get_last_month_revenue(),
            "total_revenue": StatisticService.get_total_revenue(),
        }
        return Response(statistics)
