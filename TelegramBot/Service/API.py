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


class TelegramUserSubscriptionAPI:
    def CreateUserSubscription(external_id, duration):
        return requests.post(PROXY+'create_user_subscription', data=json.dumps({
            "user_external_id": external_id,
            "subsribe_duration": duration,
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
        return requests.post(PROXY+'check_trial_users',
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
