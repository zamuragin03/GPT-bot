from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Count, Sum
from .models import TelegramUser, UserAction, AdminTelegramUser, UserSubscription, UserPromocode, Payment


from datetime import timedelta

def create_or_extend_subscription(user, sub_type):
    # Проверяем, является ли подписка пожизненной
    if sub_type.duration > 999:
        # Отключаем все действующие подписки
        active_subscriptions = UserSubscription.objects.filter(user=user, is_active=True)
        active_subscriptions.update(is_active=False)  # Массовое обновление статуса

        # Создаём новую пожизненную подписку
        lifetime_subscription = UserSubscription.objects.create(
            sub_type=sub_type,
            user=user,
            is_active=True
        )
        return {
            'status': 'lifetime subscription created',
            'subscription type': sub_type.name,
        }

    # Ищем действующую подписку
    active_subscription = UserSubscription.objects.filter(
        user=user, is_active=True
    ).first()

    if active_subscription:
        # Продляем текущую подписку
        active_subscription.till += timedelta(hours=sub_type.duration)
        active_subscription.save()
        return {
            'status': 'subscription extended',
            'subscription active till': active_subscription.till
        }
    else:
        # Создаём новую подписку
        new_subscription = UserSubscription.objects.create(
            sub_type=sub_type,
            user=user,
            is_active=True
        )
        return {
            'status': 'subscription created',
            'subscription type': sub_type.name
        }


class StatisticService:

    def get_total_users():
        return TelegramUser.objects.filter().count()

    def get_unbanned_users():
        return TelegramUser.objects.filter(is_banned=False).count()

    def get_registered_today_count():
        today = now().date()  # Получаем текущую дату
        return TelegramUser.objects.filter(created_at__date=today).count()

    def get_new_users_current_month():
        current_month = timezone.now().month
        current_year = timezone.now().year
        return TelegramUser.objects.filter(created_at__year=current_year, created_at__month=current_month).count()

    def get_new_users_last_month():
        now = timezone.now()
        last_month = (now.month - 1) if now.month > 1 else 12
        last_month_year = now.year if now.month > 1 else now.year - 1
        return TelegramUser.objects.filter(created_at__year=last_month_year, created_at__month=last_month).count()

    def current_month_subscribers_count():
        today = now()  # Текущая дата и время
        start_of_month = today.replace(day=1)  # Начало текущего месяца

        return TelegramUser.objects.filter(
            # Подписка начата с начала месяца
            usersubscription__created_at__gte=start_of_month,
            usersubscription__till__gte=today,  # Подписка все еще активна
            usersubscription__is_active=True  # Только активные подписки
        ).distinct().count()

    def last_month_subscribers_count():
        today = now()
        start_of_current_month = today.replace(day=1)  # Начало текущего месяца
        end_of_previous_month = start_of_current_month - \
            timedelta(days=1)  # Конец прошлого месяца
        start_of_previous_month = end_of_previous_month.replace(
            day=1)  # Начало прошлого месяца

        return TelegramUser.objects.filter(
            usersubscription__created_at__gte=start_of_previous_month,
            usersubscription__created_at__lte=end_of_previous_month,
            usersubscription__till__gte=start_of_previous_month,
            usersubscription__is_active=True  # Только активные подписки
        ).distinct().count()

    def today_subscribers_count():
        today = now().date()  # Текущая дата
        return TelegramUser.objects.filter(
            usersubscription__created_at__date=today,  # Подписка создана сегодня
            # Подписка активна до или после сегодняшнего дня
            usersubscription__till__date__gte=today,
            usersubscription__is_active=True  # Только активные подписки
        ).distinct().count()

    def today_subscribers_bought_count():
        today = now().date()  # Текущая дата
        return TelegramUser.objects.filter(
            usersubscription__created_at__date=today  # Подписка была создана сегодня
        ).distinct().count()

    def this_month_subscribers_bought_count():
        today = now()
        start_of_month = today.replace(day=1)  # Начало текущего месяца

        return TelegramUser.objects.filter(
            # Подписка была создана начиная с начала текущего месяца
            usersubscription__created_at__gte=start_of_month
        ).distinct().count()

    def last_month_subscribers_bought_count():
        today = now()
        start_of_current_month = today.replace(day=1)  # Начало текущего месяца
        end_of_previous_month = start_of_current_month - \
            timedelta(days=1)  # Конец прошлого месяца
        start_of_previous_month = end_of_previous_month.replace(
            day=1)  # Начало прошлого месяца

        return TelegramUser.objects.filter(
            # Подписка была создана начиная с начала прошлого месяца
            usersubscription__created_at__gte=start_of_previous_month,
            # Подписка была создана до конца прошлого месяца
            usersubscription__created_at__lte=end_of_previous_month
        ).distinct().count()

    def get_active_subscribers_count():
        return UserSubscription.objects.filter(is_active=True).count()

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
        tokens_aggregates = UserAction.objects.filter(created_at__year=current_year, created_at__month=current_month).aggregate(
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

    def get_income_yesterday():
        today = now().date()  # Текущая дата
        yesterday = today - timedelta(days=1)  # Вчерашняя дата

        return Payment.objects.filter(
            status='success',  # Учитываем только успешные платежи
            created_at__date=yesterday  # Платежи, созданные вчера
        ).aggregate(total_revenue=Sum('amount'))['total_revenue'] or 0

    def get_last_month_revenue():
        today = now()
        start_of_current_month = today.replace(day=1)  # Начало текущего месяца
        end_of_previous_month = start_of_current_month - \
            timedelta(days=1)  # Конец прошлого месяца
        start_of_previous_month = end_of_previous_month.replace(
            day=1)  # Начало прошлого месяца

        # Вычисляем сумму успешных платежей за прошлый месяц
        return Payment.objects.filter(
            status='success',  # Только успешные платежи
            created_at__gte=start_of_previous_month,  # От начала прошлого месяца
            created_at__lte=end_of_previous_month  # До конца прошлого месяца
        ).aggregate(total_revenue=Sum('amount'))['total_revenue'] or 0

    def get_total_revenue():
        # Суммируем все успешные платежи
        total_revenue = Payment.objects.filter(
            status='success'  # Только успешные платежи
        ).aggregate(total_revenue=Sum('amount'))['total_revenue'] or 0

        return total_revenue

    def get_top_referrals_last_month():
        today = now()
        start_of_current_month = today.replace(day=1)  # Начало текущего месяца
        end_of_previous_month = start_of_current_month - \
            timedelta(days=1)  # Конец прошлого месяца
        start_of_previous_month = end_of_previous_month.replace(
            day=1)  # Начало прошлого месяца

        top_referrals = TelegramUser.objects.filter(
            # Приглашенные зарегистрировались в прошлом месяце
            created_at__gte=start_of_previous_month,
            # Учитываем только до конца прошлого месяца
            created_at__lte=end_of_previous_month,
            referal__isnull=False  # Только те, кто пришли по реферальной ссылке
        ).values(
            'referal__username',  # Имя пользователя реферала
            'referal__external_id',  # ID реферала
        ).annotate(
            invite_count=Count('referal')  # Считаем количество приглашенных
        ).order_by('-invite_count')[:10]  # Сортируем по количеству приглашенных и ограничиваем до 10

        return top_referrals

    def get_top_referrals_this_month():
        start_of_month = now().replace(day=1)  # Начало текущего месяца

        top_referrals = TelegramUser.objects.filter(
            created_at__gte=start_of_month,  # Приглашенные зарегистрировались в этом месяце
            referal__isnull=False  # Только те, кто пришли по реферальной ссылке
        ).values(
            'referal__username',  # Имя пользователя реферала
            'referal__external_id',  # ID реферала
        ).annotate(
            invite_count=Count('referal')  # Считаем количество приглашенных
        ).order_by('-invite_count')[:10]  # Сортируем по количеству приглашенных и ограничиваем до 10

        return top_referrals

    def get_top_referrals_all_time():
        top_referrals = TelegramUser.objects.filter(
            referal__isnull=False  # Только те, кто пришли по реферальной ссылке
        ).values(
            'referal__username',  # Имя пользователя реферала
            'referal__external_id',  # ID реферала
        ).annotate(
            invite_count=Count('referal')  # Считаем количество приглашенных
        ).order_by('-invite_count')[:10]  # Сортируем по количеству приглашенных и ограничиваем до 10

        return top_referrals
