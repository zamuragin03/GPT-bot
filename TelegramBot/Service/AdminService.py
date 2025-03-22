from .API import AdminTelegramUserAPI


class AdminService:
    @staticmethod
    def GetAllAdminsID():
        return [el.get('external_id') for el in AdminTelegramUserAPI.GetAllAdmins().get('results')]

    @staticmethod
    def GetStatistic():
        stat_text = 'Статистика:\n'
        stat_obj = AdminTelegramUserAPI.GetStatistic()

        return stat_text + \
            f"Всего пользователей: {stat_obj.get('total_users')}\n" + \
            f"Пользователей без бана: {stat_obj.get('unbanned_users')}\n" + \
            f"Зарегистрировались сегодня: {stat_obj.get('registered_today')}\n" + \
            f"Новых пользователей в этом месяце: {stat_obj.get('new_users_current_month')}\n" + \
            f"Новых пользователей в прошлом месяце: {stat_obj.get('new_users_last_month')}\n" + \
            f"Подписчиков в этом месяце: {stat_obj.get('current_month_subscribers')}\n" + \
            f"Подписчиков в прошлом месяце: {stat_obj.get('last_month_subscribers')}\n" + \
            f"Подписчиков сегодня: {stat_obj.get('today_subscribers')}\n" + \
            f"Купили подписку сегодня: {stat_obj.get('today_subscribers_bought')}\n" + \
            f"Купили подписку в этом месяце: {stat_obj.get('this_month_subscribers_bought')}\n" + \
            f"Купили подписку в прошлом месяце: {stat_obj.get('last_month_subscribers_bought')}\n" + \
            f"Активных подписчиков: {stat_obj.get('active_subscribers')}\n" + \
            f"Количество админов: {stat_obj.get('admins_count')}\n" + \
            f"Запросов сегодня: {stat_obj.get('requests_today')}\n" + \
            f"Запросов вчера: {stat_obj.get('requests_yesterday')}\n" + \
            f"Запросов в этом месяце: {stat_obj.get('requests_current_month')}\n" + \
            f"Токенов потрачено сегодня: {stat_obj.get('tokens_spent_today')}\n" + \
            f"Токенов потрачено вчера: {stat_obj.get('tokens_spent_yesterday')}\n" + \
            f"Токенов потрачено в этом месяце: {stat_obj.get('tokens_spent_current_month')}\n" + \
            f"Токенов потрачено в прошлом месяце: {stat_obj.get('tokens_spent_last_month')}\n" + \
            f"Доход сегодня: {stat_obj.get('income_today')}₽\n" + \
            f"Доход вчера: {stat_obj.get('income_yesterday')}₽\n" + \
            f"Доход в прошлом месяце: {stat_obj.get('last_month_revenue')}₽\n" + \
            f"Общий доход: {stat_obj.get('total_revenue')}₽"

    @staticmethod
    def GetReferalStat(query_type:str):
        return AdminTelegramUserAPI.GetReferalStatistic(query_type)