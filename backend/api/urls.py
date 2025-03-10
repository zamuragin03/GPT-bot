from django.urls import *
from api.views import *

urlpatterns = [
    # tg user
    path('get_telegram_users', GetTelegramUsers.as_view()),
    path('get_telegram_user/<int:external_id>', GetTelegramUser.as_view()),
    path('create_telegram_user', CreateTelegramUser.as_view()),
    path('delete_telegram_user/<int:external_id>',
         DeleteTelegramUser.as_view()),
    path('update_telegram_user/<int:external_id>',
         UpdateTelegramUser.as_view()),
    path('get_telegram_user_referals/<int:external_id>/',
         CheckReferals.as_view(), ),

    # admin
    path('get_admins', GetAdminTelegramUsers.as_view()),

    # user subscriptions
    path('create_user_subscription', CreateUserSubscription.as_view()),
    path('get_user_subscriptions', GetUserSubscriptions.as_view()),


    # tasks
    path('check_debts', CheckDebtUsers.as_view()),

    # subscriptions
    path('get_subscription/<int:duration>', GetSubscription.as_view()),

    # user actions
    path('create_user_action', CreateUserAction.as_view()),

    # user actions
    path('activate_promocode', ActivatePromocodeView.as_view()),

    # user limits
    path('check_limits/<int:external_id>/',
         CheckUserLimitationsByExternalId.as_view(), name='check_limits'),
    
    path('check_daily_limits/<int:external_id>/',
         CheckUserActionsLast24Hours.as_view(), name='check_daily_limits'),

     #paymanets
     path('create_paymnet', CreatePayment.as_view()),
     path('get_payment/<str:order_id>', GetPayment.as_view()),
     path('update_payment/<str:order_id>', UpdatePayment.as_view()),

    # auth
    path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('drf-auth', include('rest_framework.urls')),

    # statistics
    path('statistics/', StatisticsView.as_view(), name='statistics'),
]
