from openai.types import Completion
from Config import (client,
                    DEFAULT_MODE_SYSTEM_PROMPT,
                    AI_MODELS, REASONING_EFFORT
                    )
from .LocalizationService import LocalizationService
from .UserActionService import UserActionService


class DefaultModeGPTService:
    def __init__(self, external_id, language):
        self.total_tokens_used = 0
        self.user_external_id = external_id
        self.model = AI_MODELS.GPT_4_O_MINI_2024_07_18
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
                            "text": DEFAULT_MODE_SYSTEM_PROMPT
                        }
                ],
            },
        ]

    def add_message(self, content):

        # Добавляем новое текстовое сообщение
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

    def change_reasoning_effort(self, reasoning_effort: REASONING_EFFORT):
        self.reasoning_effort = reasoning_effort

    def clear_context(self):
        self.messages = [
            {
                "role": "system",
                "content": [
                        {
                            "type": "text",
                            "text": DEFAULT_MODE_SYSTEM_PROMPT
                        }
                ]
            },
        ]
        self.total_tokens_used = 0

    def add_message_with_attachement(self, base64_image, caption):
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
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            }
                ]
            }
        )
        self.model = AI_MODELS.GPT_4_O_MINI_2024_07_18

    def set_auto_save(self, flag: bool):
        self.auto_save = flag

    def check_if_context_limit_reached(self,):
        if self.total_tokens_used > 45000:
            return True
        return False

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

    def escape_html(self, input_text):
        # Определяем шаблон для поиска разрешенных тегов
        import re
        allowed_tags = [
            r'<b>.*?</b>',
            r'<i>.*?</i>',
            r'<u>.*?</u>',
            r'<s>.*?</s>',
            r'<span class="tg-spoiler">.*?</span>',
            r'<a href="http://www.example.com/">.*?</a>',
            r'<code>.*?</code>',
            r'<pre.*?>.*?</pre>',  # Обновлен шаблон чтобы поддерживать pre с языком
            r'<code class="language-\w+">.*?</code>'
        ]

        # Создаем общий компилированный регулярных выражений для всех разрешенных тегов
        allowed_pattern = '|'.join(allowed_tags)

        def replace_function(text):
            # Экранирование неразрешённого контента
            # Escape & except like &amp;
            text = re.sub(r'&(?![#\w]+;)', '&amp;', text)
            text = text.replace('<', '&lt;').replace('>', '&gt;')
            return text

        parts = re.split(f'({allowed_pattern})', input_text, flags=re.DOTALL)
        escaped_result = [part if re.fullmatch(
            allowed_pattern, part, flags=re.DOTALL) else replace_function(part) for part in parts]

        return ''.join(escaped_result).replace('<br>', '').replace('<br/>', '')

    async def generate_response(self):

        response: Completion = None
        if self.model == AI_MODELS.O_3_MINI.value:
            response = await client.chat.completions.create(
                model=self.model.value,
                messages=list(filter(lambda x: not any(
                    item['type'] == 'image_url' for item in x['content']), self.messages)),
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
        result_text = LocalizationService.BotTexts.GetPrefixByName(
            self.action_type_name, self.language)
        result_text += self.escape_html(response.choices[0].message.content)
        return result_text
