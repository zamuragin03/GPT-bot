
import re
import asyncio
from Config import (client,
                    ESSAY_WORK_SYSTEM_PROMPT_FOR_PLAN,
                    ESSAY_WORK_BODY_SYSTEM_PROMPT,
                    ESSAY_BODY_INSTRUCTIONS
                    )
from .UserActionService import UserActionService


import re
import asyncio


class EssayGPTService:
    def __init__(self, external_id, topic, page_number):
        self.user_external_id = external_id
        self.page_number = page_number
        self.model = "gpt-4o"
        self.action_type_name = 'essay_helper'
        self.input_tokens = 0
        self.output_tokens = 0
        self.retries_count = 0
        self.retries_manual_count = 0
        self.topic = topic
        self.init_body_messages = []
        self.init_plan_messages = self.create_system_message(
            ESSAY_WORK_SYSTEM_PROMPT_FOR_PLAN)

    def create_system_message(self, prompt):
        return [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            },
        ]

    def append_user_message(self, message_list: list, user_text):
        message_list.append(
            {
                "role": 'user',
                "content": [
                    {
                        "type": "text",
                        "text": user_text
                    }
                ]
            },
        )

    def is_retries_allowed(self, is_manual=False):
        if is_manual:
            return self.retries_manual_count < 3
        return self.retries_count < 3

    def append_assistant_message(self, message_list: list, assistant_text):
        message_list.append(
            {
                "role": 'assistant',
                "content": [
                    {
                        "type": "text",
                        "text": assistant_text
                    }
                ]
            },
        )

    def update_tokens(self, response):
        self.input_tokens += response.usage.prompt_tokens
        self.output_tokens += response.usage.completion_tokens

    def get_initial_plan(self):
        self.append_user_message(
            self.init_plan_messages, f'Напиши план для эссе по теме {self.topic}')

    async def get_plan_response(self):
        response = await client.chat.completions.create(
            model=self.model,
            messages=self.init_plan_messages
        )

        self.update_tokens(response)

        plan = response.choices[0].message.content
        self.append_assistant_message(self.init_plan_messages, plan)
        self.plan = plan
        self.init_body_messages = self.create_system_message(
            ESSAY_WORK_BODY_SYSTEM_PROMPT.format(
                topic=self.topic, plan=self.plan, page_number=self.page_number*3, ESSAY_BODY_INSTRUCTIONS=ESSAY_BODY_INSTRUCTIONS)
        )
        return self.plan

    def regenerate_plan(self):
        self.retries_count += 1
        self.append_user_message(
            self.init_plan_messages, 'Сгенерируй другой план')

    def regenerate_plan_with_user_detail(self, user_message):
        self.retries_manual_count += 1
        self.append_user_message(
            self.init_plan_messages, f'Сгенерируй другой план с учетом пожелания пользователя:{user_message}. Если считаешь пожелание пользователя неадекватным, то просто сгенерируй новый план')

    @staticmethod
    def extract_headers(text):
        headers_pattern = re.compile(r"(<h[12]>.*?<\/h[12]>)")
        headers = headers_pattern.findall(text)
        return headers

    # это метод для написания каждого параграфа
    async def write_chapter(self, chapter_name):
        self.append_user_message(
            self.init_body_messages, f'Напиши текст для раздела "{chapter_name}"')
        # if str(chapter_name).startswith('<h1>'):
        #     self.append_assistant_message(
        #         self.init_body_messages, chapter_name)
        #     return
        response = await client.chat.completions.create(
            model=self.model,
            messages=self.init_body_messages
        )
        self.update_tokens(response)
        self.append_assistant_message(
            self.init_body_messages, response.choices[0].message.content)

    async def build_essay_work(self):
        self.list_of_chapters = EssayGPTService.extract_headers(
            self.plan)
        for chapter in self.list_of_chapters:
            await self.write_chapter(chapter)
        UserActionService.CreateUserAction(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            prompt=self.topic,
            model_open_ai_name=self.model,
            action_type_name=self.action_type_name,
            user_external_id=self.user_external_id
        )
        return list(filter(lambda x: x.get('role') == 'assistant', self.init_body_messages))
