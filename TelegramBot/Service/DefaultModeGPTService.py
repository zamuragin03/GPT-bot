from openai.types import Completion
from Config import (client,
                    DEFAULT_MODE_SYSTEM_PROMPT, NEW_DEFAULT_MODE_SYSTEM_PROMPT,

                    AI_MODELS, REASONING_EFFORT
                    )
from .LocalizationService import LocalizationService
from .BotService import BotService
from .UserActionService import UserActionService



class DefaultModeGPTService:
    def __init__(self, external_id, language):
        self.total_tokens_used = 0
        self.user_external_id = external_id
        self.model = AI_MODELS.GPT_4_O_MINI
        self.reasoning_effort = REASONING_EFFORT.MEDIUM
        self.auto_save = True
        self.CONTEXT_LIMIT = 200_000
        self.action_type_name = 'default_mode'
        self.language = language
        self.messages = [
            {
                "role": "system",
                "content": NEW_DEFAULT_MODE_SYSTEM_PROMPT
            },
        ]

    def add_message(self, content):

        # Добавляем новое текстовое сообщение
        self.messages.append(
            {
                "role": "user",
                "content":  content
            }
        )

    def add_file_message(self, file_content, caption=''):

        # Добавляем новое текстовое сообщение
        self.messages.append(
            {
                "role": "user",
                "content":  f'{caption}, {file_content}'
            }
        )

    def add_ai_message(self, content):
        self.messages.append(
            {
                "role": "assistant",
                "content": content
            }
        )

    def change_reasoning_effort(self, reasoning_effort: REASONING_EFFORT):
        self.reasoning_effort = reasoning_effort

    def clear_context(self):
        self.messages = [
            {
                "role": "system",
                "content": DEFAULT_MODE_SYSTEM_PROMPT
            }
        ]
        self.total_tokens_used = 0

    def add_message_with_attachement(self, base64_image='', caption=''):
        self.messages.append(
            {
                "role": "user",
                "content": [
                        {
                            "type": "text",
                            "text": caption
                        },
                    {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        )

    def set_auto_save(self, flag: bool):
        self.auto_save = flag

    def check_if_context_limit_reached(self,):
        if self.total_tokens_used > self.CONTEXT_LIMIT:
            return True
        return False

    def add_action(self, response: Completion):
        self.total_tokens_used += response.usage.total_tokens

        last_message = list(filter(lambda x: x.get(
            'role') == 'user', self.messages))[-1].get('content')
        if isinstance(last_message, list):
            last_message = last_message[0].get('text')
        UserActionService.CreateUserAction(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            prompt=last_message,
            model_open_ai_name=self.model.value,
            action_type_name=self.action_type_name,
            user_external_id=self.user_external_id
        )

    async def generate_response(self):
        payload = {
            "model": self.model.value,
            "messages": self.messages,  #
            "response_format": {
                "type": "text",
            },
            "temperature": 0.2,           # Оптимальный баланс креативности/точности
            "max_completion_tokens": 2048,  # Резерв для системных токенов
            "top_p": 0.95,                 # Широкая выборка с фильтрацией
            "frequency_penalty": 0,      # Борьба с повторами
            "presence_penalty": 0,       # Поощрение новых идей
            "logit_bias": {6762: 100,  # Для токена "▎"
                           236: 100,   # Для дополнительного токена "▎"
                           27: 50,     # Для первой части токена "<pre>"
                           2235: 50,   # Для второй части токена "<pre>"
                           29: 50},
            "store": False
        }

        try:
            # Send the API request
            response = await client.chat.completions.create(**payload)

            # Add assistant response to messages
            self.add_ai_message(response.choices[0].message.content)

            if not self.auto_save:
                self.clear_context()

            self.add_action(response)

            # Escape HTML for safe output
            postfix_text = LocalizationService.BotTexts.GetPrefixByName(
                self.action_type_name, self.language
            )
            with open('text.txt', 'w', encoding='utf-8') as f:
                f.write(str(response.choices[0].message.content))
                 
            result_text = BotService.escape_html(
                BotService.sanitize_response(
                    response.choices[0].message.content)
            )
            return result_text+postfix_text

        except Exception as e:
            return "Unresolved error. Please try again later. Error log: " + str(e)
