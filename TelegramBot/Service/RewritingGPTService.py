from openai.types import Completion
from Config import (
    client,
    REWRITING_STYSTEM_PROMPT,
    AI_MODELS,
    REASONING_EFFORT
)
from .UserActionService import UserActionService


class RewritingGPTService:
    def __init__(self, external_id, language):
        self.total_tokens_used = 0
        self.user_external_id = external_id
        self.model = AI_MODELS.O_3_MINI
        self.reasoning_effort = REASONING_EFFORT.MEDIUM
        self.auto_save = True
        self.action_type_name = 'default_mode'
        self.language = language
        self.messages = [
            {
                "role": "system",
                "content": [
                        {
                            "type": "text",
                            "text": REWRITING_STYSTEM_PROMPT
                        }
                ],
            },
        ]

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

    def add_action(self, response: Completion):
        self.total_tokens_used += response.usage.total_tokens
        last_message = list(filter(lambda x: x.get(
            'role') == 'user', self.messages))[-1].get('content')[0].get('text')
        UserActionService.CreateUserAction(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            prompt=last_message,
            model_open_ai_name=self.model.value,
            action_type_name=self.action_type_name,
            user_external_id=self.user_external_id
        )

    async def generate_response(self):
        response = await client.chat.completions.create(
                model=self.model.value,
                messages=self.messages,
                response_format={
                    "type": "text"
                },
            )
        self.add_action(response)
        return response.choices[0].message.content
