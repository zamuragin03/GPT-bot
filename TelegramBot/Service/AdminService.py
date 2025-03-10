from .API import AdminTelegramUserAPI


class AdminService:
    @staticmethod
    def GetAllAdminsID():
        return [el.get('external_id') for el in AdminTelegramUserAPI.GetAllAdmins().get('results')]

    @staticmethod
    def GetStatistic():
        stat_text = 'Статистика:\n'
        stat_obj = AdminTelegramUserAPI.GetStatistic()
        return stat_text + f"Активных пользователей: {stat_obj.get('alive_users')}\n" + \
            f"Активных пользователей сегодня: {stat_obj.get('active_users_today')}\n" + \
            f"Новых пользователей в этом месяце: {stat_obj.get('new_users_current_month')}\n" + \
            f"Новых пользователей в прошлом месяце: {stat_obj.get('new_users_last_month')}\n" + \
            f"Пользователей через рефералку: {stat_obj.get('users_via_referral')}\n" + \
            f"Количество админов: {stat_obj.get('admins_count')}\n" + \
            f"Запросов сегодня: {stat_obj.get('requests_today')}\n" + \
            f"Запросов вчера: {stat_obj.get('requests_yesterday')}\n" + \
            f"Запросов в этом месяце: {stat_obj.get('requests_current_month')}\n" + \
            f"Токенов потрачено сегодня: {stat_obj.get('tokens_spent_today')}\n" + \
            f"Токенов потрачено вчера: {stat_obj.get('tokens_spent_yesterday')}\n" + \
            f"Токенов потрачено в этом месяце: {stat_obj.get('tokens_spent_current_month')}\n" + \
            f"Токенов потрачено в прошлом месяце: {stat_obj.get('tokens_spent_last_month')}\n" + \
            f"Доход сегодня: {stat_obj.get('income_today')}"
