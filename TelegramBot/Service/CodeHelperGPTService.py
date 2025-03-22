from Config import (CODE_HELPER_SYSTEM_PROMPT,
                    client,
                    AI_MODELS, REASONING_EFFORT
                    )
from .UserActionService import UserActionService
from openai.types import Completion


class CodeHelperGPTService:
    def __init__(self, external_id):
        self.external_id = external_id
        self.total_tokens_used = 43000
        self.model = AI_MODELS.O_3_MINI
        self.reasoning_effort = REASONING_EFFORT.MEDIUM
        self.auto_save = True
        self.action_type_name = 'code_helper'
        self.messages = [
            {
                "role": "system",
                "content": [
                        {
                            "type": "text",
                            "text": CODE_HELPER_SYSTEM_PROMPT
                        }
                ],
            },
        ]

    def add_action(self, response: Completion,):
        self.total_tokens_used += response.usage.total_tokens
        last_message = list(filter(lambda x: x.get(
            'role') == 'user', self.messages))[-1].get('content')[0].get('text')
        UserActionService.CreateUserAction(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            prompt=last_message,
            model_open_ai_name=self.model.value,
            action_type_name=self.action_type_name,
            user_external_id=self.external_id
        )

    def change_reasoning_effort(self, reasoning_effort: REASONING_EFFORT):
        self.reasoning_effort = reasoning_effort

    def clear_context(self):
        self.messages = [
            {
                "role": "system",
                "content": [
                        {
                            "type": "text",
                            "text": CODE_HELPER_SYSTEM_PROMPT
                        }
                ],
            },
        ]

    def set_auto_save(self, flag: bool):
        self.auto_save = flag

    def add_message(self, content):

        self.messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": content
                    }
                ]
            }
        )
        # Устанавливаем модель для текстового сообщения

    def add_ai_message(self, content):
        self.messages.append(
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content
                    }
                ]
            }
        )

    def check_if_context_limit_reached(self,):
        if self.total_tokens_used > 45000:
            return True

    async def generate_response(self):
        response = await client.chat.completions.create(
            model=self.model.value,
            messages=self.messages,
            response_format={
                "type": "text"
            },
            reasoning_effort=self.reasoning_effort.value,  # Передается только для 3o-mini
        )
        self.add_ai_message(response.choices[0].message.content)
        if not self.auto_save:
            self.clear_context()
        self.add_action(response)
        result_text = 'Здравствуйте! Я <a href="https://t.me/student_helpergpt_bot">StudentHelper</a>,  персональный помощник в написании и редактировании кода 👨‍💻\n\n'
        result_text += response.choices[0].message.content
        return result_text
