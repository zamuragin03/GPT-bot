from django.contrib import admin
from .models import *
from django.utils.html import mark_safe
admin.site.site_header = "Бот для учета работы StudyGPT"
admin.site.site_title = "Админка бота"


class AdminTelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'external_id',
    ]
    list_per_page = 100
    list_display_links = list_display


class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'Потрачено_Токенов',
        'external_id',
        'username',
        'first_name',
        'last_name',
        'created_at',
        'balance',
    ]
    readonly_fields = ('created_at',)
    list_per_page = 100
    list_display_links = list_display

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
    list_display_links = list_display


class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
        'duration',
        'price'
    ]
    list_display_links = list_display


class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'sub_type',
        'user',
        'is_active',
        'created_at',
    ]
    readonly_fields = ('created_at',)
    list_display_links = list_display
    actions = (
        'disable_subscription',
    )

    @admin.display(description='Отключить попдиску',)
    def disable_subscription(self, request, queryset):
        queryset.update(is_active=False)


admin.site.register(AdminUser, AdminTelegramUserAdmin)
admin.site.register(TelegramUser, TelegramUserAdmin)
admin.site.register(AIModel, AiModelAdmin)
admin.site.register(ActionType, ActionTypeAdmin)
admin.site.register(UserAction, UserActionAdmin)
admin.site.register(SubscriptionType, SubscriptionTypeAdmin)
admin.site.register(UserSubscription, UserSubscriptionAdmin)
