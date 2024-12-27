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

    # user subscriptions
    path('create_user_subscription', CreateUserSubscription.as_view()),
    path('get_user_subscriptions', GetUserSubscriptions.as_view()),


    # tasks
    path('check_trial_users', CheckTrialDebtUsers.as_view()),


    # user actions
    path('create_user_action', CreateUserAction.as_view()),

    # user limits
    
    path('check_limits/<int:external_id>/', CheckUserLimitationsByExternalId.as_view(), name='check_limits'),

    # auth
    path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('drf-auth', include('rest_framework.urls')),

]
