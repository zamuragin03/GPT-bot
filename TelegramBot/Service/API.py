import uuid
import requests
from Config import PROXY, AUTH_TOKEN
import json
import json


class TGUSerApi:
    def CreateTelegramUser(external_id, username, first_name, second_name, ref_external_id=None):
        requests.post(PROXY+'create_telegram_user', data=json.dumps({
            "external_id": external_id,
            "username": username,
            "first_name": first_name,
            "second_name": second_name,
            "ref_external_id": ref_external_id
        }), headers={"Content-type": "application/json",
                     "Authorization": f"Token {AUTH_TOKEN}"},
        )

    def GetTelegramUser(external_id) -> dict:
        return requests.get(PROXY+'get_telegram_user/' + str(external_id),
                            headers={"Content-type": "application/json",
                                     "Authorization": f"Token {AUTH_TOKEN}"},
                            ).json()

    def UpdateTelegramUser(external_id, **kwargs):
        return requests.patch(PROXY+'update_telegram_user/'+str(external_id), data=kwargs,
                              headers={"Content-type": "application/json",
                                       "Authorization": f"Token {AUTH_TOKEN}"},
                              )

    def GetTelegramUsersReferals(external_id, ):
        return requests.get(PROXY+'get_telegram_user_referals/'+str(external_id),
                            headers={"Content-type": "application/json",
                                     "Authorization": f"Token {AUTH_TOKEN}"},
                            ).json()

    def GetAllTelegramUsers():
        return requests.get(PROXY+'get_telegram_users',
                            headers={"Content-type": "application/json",
                                     "Authorization": f"Token {AUTH_TOKEN}"},
                            ).json()


class TelegramUserSubscriptionAPI:
    def CreateUserSubscription(external_id, duration):
        return requests.post(PROXY+'create_user_subscription', data=json.dumps({
            "user_external_id": external_id,
            "subscribe_duration": duration,
        }),
            headers={"Content-type": "application/json",
                     "Authorization": f"Token {AUTH_TOKEN}"},
        )

    def GetUserSubscriptions(**kwargs) -> list:
        return requests.get(PROXY+'get_user_subscriptions', params=kwargs,
                            headers={"Content-type": "application/json",
                                     "Authorization": f"Token {AUTH_TOKEN}"},
                            ).json()

    def GetDebtUsers() -> dict:
        return requests.post(PROXY+'check_debts',
                             headers={"Content-type": "application/json",
                                      "Authorization": f"Token {AUTH_TOKEN}"},
                             ).json()

    def GetUserLimitations(external_id) -> dict:
        return requests.get(PROXY+f'check_limits/{external_id}',
                            headers={"Content-type": "application/json",
                                     "Authorization": f"Token {AUTH_TOKEN}"},
                            ).json()
        
    def GetUserDailyLimitations(external_id) -> dict:
        return requests.get(PROXY+f'check_daily_limits/{external_id}',
                            headers={"Content-type": "application/json",
                                     "Authorization": f"Token {AUTH_TOKEN}"},
                            ).json()


class UserActionAPI:
    def CreateUserAction(
            input_tokens,
            output_tokens,
            prompt,
            model_open_ai_name,
            action_type_name,
            user_external_id,
    ):
        return requests.post(PROXY+'create_user_action',
                             data=json.dumps({
                                 "input_tokens": input_tokens,
                                 "output_tokens": output_tokens,
                                 "prompt": prompt,
                                 "model_open_ai_name": model_open_ai_name,
                                 "action_type_name": action_type_name,
                                 "user_external_id": user_external_id,

                             }),
                             headers={"Content-type": "application/json",
                                      "Authorization": f"Token {AUTH_TOKEN}"},
                             )


class SubscriptionTypeAPI:
    def GetSubscriptionByDuration(duration: int) -> dict:
        return requests.get(PROXY+'get_subscription/' + str(duration),
                            headers={"Content-type": "application/json",
                                     "Authorization": f"Token {AUTH_TOKEN}"},
                            ).json()


class AdminTelegramUserAPI:
    def GetAllAdmins() -> dict:
        return requests.get(PROXY+'get_admins',
                            headers={"Content-type": "application/json",
                                     "Authorization": f"Token {AUTH_TOKEN}"},
                            ).json()

    def GetStatistic() -> dict:
        return requests.get(PROXY+'statistics',
                            headers={"Content-type": "application/json",
                                     "Authorization": f"Token {AUTH_TOKEN}"},
                            ).json()


class PromocodeAPI:
    def ActivatePromocode(
        external_id: int,
        promocode_text: uuid
    ) -> requests.Response:
        return requests.post(PROXY+'activate_promocode',
                             data=json.dumps({
                                 "external_id": external_id,
                                 "promocode_text": promocode_text,

                             }),
                             headers={"Content-type": "application/json",
                                      "Authorization": f"Token {AUTH_TOKEN}"},
                             )


class PaymentAPI:
    def CreatePayment(
        external_id: int,
        order_id: uuid,
        amount: int
    ) -> requests.Response:
        return requests.post(PROXY+'create_paymnet',
                             data=json.dumps({
                                 "external_id": external_id,
                                 "order_id": order_id,
                                 "amount": amount,

                             }),
                             headers={"Content-type": "application/json",
                                      "Authorization": f"Token {AUTH_TOKEN}"},
                             )

    def UpdatePayment(**kwargs):
        return requests.patch(PROXY+'update_payment/'+str(kwargs['order_id']), data=kwargs,
                              headers={
            "Authorization": f"Token {AUTH_TOKEN}"},
        )
