from .API import UserActionAPI


class UserActionService:

    @staticmethod
    def CreateUserAction(
        input_tokens,
            output_tokens,
            prompt,
            model_open_ai_name,
            action_type_name,
            user_external_id,
    ):
        return UserActionAPI.CreateUserAction(input_tokens,
                                              output_tokens,
                                              prompt,
                                              model_open_ai_name,
                                              action_type_name,
                                              user_external_id)
