from django.db import models
from django.db.models import Sum

class AdminUser(models.Model):
    external_id = models.BigIntegerField(verbose_name='tg_id')

    def __str__(self) -> str:
        return str(self.external_id)

    class Meta:
        verbose_name = 'Админ'
        verbose_name_plural = 'Админы'


class TelegramUser(models.Model):
    external_id = models.BigIntegerField(null=False, unique=True)
    username = models.CharField(null=True, max_length=256, blank=True)
    first_name = models.CharField(null=True, max_length=256, blank=True)
    last_name = models.CharField(null=True, max_length=256, blank=True)
    balance = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True,)
    referal = models.ForeignKey(
        to='TelegramUser', on_delete=models.CASCADE, null=True, blank=True, default=None, )

    def __str__(self) -> str:
        if self.username is not None:
            return self.username
        return str(self.external_id)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class AIModel(models.Model):
    name = models.CharField(max_length=250)
    open_ai_name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"{self.name}({self.open_ai_name})"

    class Meta:
        verbose_name = 'ИИ Модель'
        verbose_name_plural = 'ИИ Модели'


class ActionType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = 'Тип запроса'
        verbose_name_plural = 'Типы запроса'


class UserAction(models.Model):
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    model = models.ForeignKey(
        to=AIModel, on_delete=models.CASCADE, null=False, blank=False, default=1)
    prompt = models.TextField(null=True, blank=True)
    action_type = models.ForeignKey(
        to=ActionType, on_delete=models.CASCADE, null=False, blank=False, default=1)
    user = models.ForeignKey(
        to=TelegramUser, on_delete=models.CASCADE, null=False, blank=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.first_name} – {self.action_type.name} – {self.action_type.name}"

    class Meta:
        verbose_name = 'Действие пользователя'
        verbose_name_plural = 'Действия пользователя'


class SubscriptionType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    duration = models.IntegerField(verbose_name='Длительность(часы)')
    price = models.IntegerField(default=0, verbose_name='Стоимость')

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = 'Типы подписок'
        verbose_name_plural = 'Типы подписок'


class UserSubscription(models.Model):
    sub_type = models.ForeignKey(
        to=SubscriptionType, on_delete=models.CASCADE, null=False, blank=False, )
    user = models.ForeignKey(
        to=TelegramUser, on_delete=models.CASCADE, null=False, blank=False, )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.user.username} – {self.sub_type.name} "

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
