from Config import (CODE_HELPER_SYSTEM_PROMPT,
                    client,
                    AI_MODELS, REASONING_EFFORT
                    )
from .UserActionService import UserActionService
from .LocalizationService import LocalizationService
from .BotService import BotService
from openai.types import Completion
from openai import AsyncStream
from aiogram.types import Message


class CodeHelperGPTService:
    def __init__(self, external_id, language):
        self.external_id = external_id
        self.total_tokens_used = 0
        self.model = AI_MODELS.GPT_4_O
        self.reasoning_effort = REASONING_EFFORT.MEDIUM
        self.auto_save = True
        self.CONTEXT_LIMIT = 200_000
        self.language = language
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

    def change_reasoning_effort(self, reasoning_effort: str):
        try:
            # Преобразуем строку в соответствующее значение Enum
            # Используем .upper() для сопоставления регистров
            self.reasoning_effort = REASONING_EFFORT[reasoning_effort.upper()]
        except KeyError:
            # Если строка не соответствует ни одному значению Enum, обработаем ошибку
            print(
                f"Invalid reasoning effort: {reasoning_effort}. Allowed values are: {', '.join(e.name.lower() for e in REASONING_EFFORT)}")

    def clear_context(self):
        self.total_tokens_used = 0
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

    def add_file_message(self, code_text, caption):
        if caption:
            self.add_message(f'{caption}: {code_text}')
        else:
            self.add_message(f'Вот мой код: {code_text}')

    def check_if_context_limit_reached(self,):
        if self.total_tokens_used > self.CONTEXT_LIMIT:
            return True

    async def generate_response(self):
        response: Completion = None
        if self.model == AI_MODELS.O_3_MINI.value:
            response = await client.chat.completions.create(
                model=self.model.value,
                messages=list(filter(lambda x: not any(
                    item['type'] == 'image_url' or item['file'] == 'file' for item in x['content']), self.messages)),
                response_format={
                    "type": "text"
                },
                reasoning_effort=self.reasoning_effort.value,  # Передается только для 3o-mini
            )
        else:
            response = await client.chat.completions.create(
                model=self.model.value,
                messages=self.messages,
                response_format={
                    "type": "text"
                },
            )
        self.add_ai_message(response.choices[0].message.content)
        if not self.auto_save:
            self.clear_context()
        self.add_action(response)
        postfix_text = LocalizationService.BotTexts.GetPrefixByName(
            self.action_type_name, self.language)
        result_text = BotService.escape_html(
            response.choices[0].message.content)
        return result_text+postfix_text

    async def send_streaming_message(self, start_message: Message):
        stream: AsyncStream = None
        accumulated_text = ""  # Будем накапливать текст по частям
        filtered_messages = list(filter(
            lambda x: not any(item.get('type') == 'image_url' or item.get('file') == 'file'
                              for item in x.get('content', [])),
            self.messages
        ))

        if self.model == AI_MODELS.O_3_MINI:
            stream = await client.chat.completions.create(
                model=self.model.value,
                messages=filtered_messages,
                stream=True,
                response_format={"type": "text"},
                reasoning_effort=self.reasoning_effort.value
            )
        else:
            stream = await client.chat.completions.create(
                model=self.model.value,
                messages=self.messages,
                stream=True,
                response_format={"type": "text"},
            )

        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                token_text = chunk.choices[0].delta.content
                accumulated_text += token_text
                yield self.escape_html(accumulated_text)

        self.add_ai_message(accumulated_text)
        if not self.auto_save:
            self.clear_context()
