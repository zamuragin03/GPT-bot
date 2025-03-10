from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Sum
from .models import TelegramUser, UserAction, AdminTelegramUser, UserSubscription, UserPromocode, Payment


def create_or_extend_subscription(user, sub_type):
    active_subscription = UserSubscription.objects.filter(
        user=user, is_active=True).first()
    if active_subscription:
        active_subscription.till += timedelta(hours=sub_type.duration)
        active_subscription.save()
        return {'status': 'subscription extended', 'subscribtion active till': active_subscription.till}
    else:
        UserSubscription.objects.create(
            sub_type=sub_type,
            user=user,
            is_active=True
        )
        return {'status': 'subscription created'}


class StatisticService:

    def get_alive_users_count():
        return TelegramUser.objects.filter(is_banned=False).count()

    def get_active_users_today():
        today = timezone.now().date()
    # Получаем количество уникальных пользователей, у которых есть действия за сегодняшний день
        return UserAction.objects.filter(created_at__date=today).values('user').distinct().count()

    def get_new_users_current_month():
        current_month = timezone.now().month
        current_year = timezone.now().year
        return TelegramUser.objects.filter(created_at__year=current_year, created_at__month=current_month).count()

    def get_new_users_last_month():
        now = timezone.now()
        last_month = (now.month - 1) if now.month > 1 else 12
        last_month_year = now.year if now.month > 1 else now.year - 1
        return TelegramUser.objects.filter(created_at__year=last_month_year, created_at__month=last_month).count()

    def get_users_via_referral():
        return TelegramUser.objects.filter(referal__isnull=False).count()

    def get_admins_count():
        return AdminTelegramUser.objects.count()

    def get_requests_today():
        today = timezone.now().date()
        return UserAction.objects.filter(created_at__date=today).count()

    def get_requests_yesterday():
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        return UserAction.objects.filter(created_at__date=yesterday).count()

    def get_requests_current_month():
        current_month = timezone.now().month
        current_year = timezone.now().year
        return UserAction.objects.filter(created_at__year=current_year, created_at__month=current_month).count()

    def get_tokens_spent_today():
        today = timezone.now().date()

        tokens_aggregates = UserAction.objects.filter(created_at__date=today).aggregate(
            total_input_tokens=Sum('input_tokens'),
            total_output_tokens=Sum('output_tokens')
        )

        # Избегаем случая, когда значения могут быть None, возвращая 0 вместо None.
        total_input_tokens = tokens_aggregates.get('total_input_tokens') or 0
        total_output_tokens = tokens_aggregates.get('total_output_tokens') or 0

        # Возвращаем сумму всех потраченных токенов
        return total_input_tokens + total_output_tokens

    def get_tokens_spent_yesterday():
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        tokens_aggregates = UserAction.objects.filter(created_at__date=yesterday).aggregate(
            total_input_tokens=Sum('input_tokens'),
            total_output_tokens=Sum('output_tokens')
        )

        # Избегаем случая, когда значения могут быть None, возвращая 0 вместо None.
        total_input_tokens = tokens_aggregates.get('total_input_tokens') or 0
        total_output_tokens = tokens_aggregates.get('total_output_tokens') or 0
        return total_input_tokens + total_output_tokens

    def get_tokens_spent_current_month():
        current_month = timezone.now().month
        current_year = timezone.now().year
        tokens_aggregates= UserAction.objects.filter(created_at__year=current_year, created_at__month=current_month).aggregate(
            total_input_tokens=Sum('input_tokens'),
            total_output_tokens=Sum('output_tokens')
        )
        # Избегаем случая, когда значения могут быть None, возвращая 0 вместо None.
        total_input_tokens = tokens_aggregates.get('total_input_tokens') or 0
        total_output_tokens = tokens_aggregates.get('total_output_tokens') or 0

        return total_input_tokens + total_output_tokens

    def get_tokens_spent_last_month():
        now = timezone.now()
        last_month = (now.month - 1) if now.month > 1 else 12
        last_month_year = now.year if now.month > 1 else now.year - 1
        tokens_aggregate = UserAction.objects.filter(created_at__year=last_month_year, created_at__month=last_month).aggregate(
            total_input_tokens=Sum('input_tokens'),
            total_output_tokens=Sum('output_tokens')
        )
        total_input_tokens = tokens_aggregate.get('total_input_tokens') or 0
        total_output_tokens = tokens_aggregate.get('total_output_tokens') or 0

        return total_input_tokens + total_output_tokens

    def get_income_today():
        today = timezone.now().date()
        
        # Фильтруем платежи по дате и статусу
        income_data = Payment.objects.filter(
            created_at__date=today,
            status='success'
        ).aggregate(total_income=Sum('amount'))
        
        # Достаем полученную сумму или 0, если ничего нет
        total_income = income_data.get('total_income') or 0.0
        
        return total_income
