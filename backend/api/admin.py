from django.contrib import admin
from .models import *
from django.utils.html import mark_safe
admin.site.site_header = "Бот для учета работы StudyGPT"
admin.site.site_title = "Админка бота"


class AdminTelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'external_id',
        'username'
    ]
    list_per_page = 100
    list_display_links = list_display


class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'username',
        'Потрачено_Токенов',
        'Количество_Приглашенных',
        'is_banned',
        'external_id',
        'first_name',
        'last_name',
        'created_at',
        'balance',
    ]
    show_full_result_count = True
    search_fields = ('pk', 'external_id')
    readonly_fields = ('created_at',)
    list_per_page = 100
    list_display_links = list(filter(
        lambda x: x not in ['external_id'], list_display))
    actions = (
        'ban_user',
        'unban_user'
    )

    def Потрачено_Токенов(self, object: TelegramUser):
        user_actions = UserAction.objects.filter(user=object)
        total_input_tokens = user_actions.aggregate(Sum('input_tokens'))[
            'input_tokens__sum'] or 0
        total_output_tokens = user_actions.aggregate(Sum('output_tokens'))[
            'output_tokens__sum'] or 0
        tokens_spent = total_input_tokens + total_output_tokens
        return mark_safe(f"<h4 style='text-align:center'>{tokens_spent}</h4>")

    def Количество_Приглашенных(self, object: TelegramUser):
        count = TelegramUser.objects.filter(referal=object).count()
        return mark_safe(f"<h1 style='text-align:center'>{count}</h1>")

    @admin.display(description='Заблокировать пользователей',)
    def ban_user(self, request, queryset):
        queryset.update(is_banned=True)

    @admin.display(description='Разблокировать пользователей',)
    def unban_user(self, request, queryset):
        queryset.update(is_banned=False)


class AiModelAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
        'open_ai_name',
    ]
    list_display_links = list_display


class ActionTypeAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
    ]
    list_filter = (
        'name',
    )
    list_display_links = list_display


class UserActionAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'input_tokens',
        'output_tokens',
        'model',
        'prompt',
        'action_type',
        'user',
        'created_at',
        'updated_at'
    ]
    list_filter = (
        'model',
        'user',
        'created_at',
    )
    preserve_filters = True
    list_display_links = list_display


class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
        'duration',
        'price'
    ]
    readonly_fields = (
        'duration',
    )
    list_display_links = list_display


class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'sub_type',
        'user',
        'is_active',
        'created_at',
        'till'
    ]
    readonly_fields = ('created_at', 'till')
    list_display_links = list_display
    actions = (
        'disable_subscription',
    )
    list_filter = (
        'is_active',
        'user',
    )

    @admin.display(description='Отключить попдиску',)
    def disable_subscription(self, request, queryset):
        queryset.update(is_active=False)


class UserPromocodeAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'promocode_text',
        'sub_type',
        'is_active',
        'created_at',
        'updated_at'
    ]
    list_per_page = 100
    list_display_links = list(filter(
        lambda x: x not in ['promocode_text'], list_display))


class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'status',
        'amount',
        'user',
        'created_at',
        'updated_at',
        'order_id',
    ]
    list_display_links = list_display
    list_filter = (
        'status',
        'user',
    )
    list_per_page = 100


admin.site.register(Payment, PaymentAdmin)
admin.site.register(UserPromocode, UserPromocodeAdmin)
admin.site.register(AdminTelegramUser, AdminTelegramUserAdmin)
admin.site.register(TelegramUser, TelegramUserAdmin)
admin.site.register(AIModel, AiModelAdmin)
admin.site.register(ActionType, ActionTypeAdmin)
admin.site.register(UserAction, UserActionAdmin)
admin.site.register(SubscriptionType, SubscriptionTypeAdmin)
admin.site.register(UserSubscription, UserSubscriptionAdmin)
