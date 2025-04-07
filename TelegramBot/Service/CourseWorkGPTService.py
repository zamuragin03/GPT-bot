import re
import asyncio
from Config import (client,
                    COURSE_WORK_SYSTEM_PROMPT_FOR_PLAN,
                    COURSE_WORK_BODY_SYSTEM_PROMPT,
                    )
from DataModels.AbstractDataModel import PlanResponse, ParagraphResponse
from langchain.output_parsers import PydanticOutputParser
from .UserActionService import UserActionService


class CourseWorkGPTService:
    def __init__(self, external_id, topic, page_number):
        self.user_external_id = external_id
        self.page_number = page_number
        self.model = "gpt-4o"
        self.action_type_name = 'course_work_helper'
        self.plan_parser = PydanticOutputParser(pydantic_object=PlanResponse)
        self.paragraph_parser = PydanticOutputParser(
            pydantic_object=ParagraphResponse)
        self.input_tokens = 0
        self.output_tokens = 0
        self.retries_count = 0
        self.retries_manual_count = 0
        self.topic = topic
        self.init_body_messages = []
        self.init_plan_messages = self.create_system_message(
            COURSE_WORK_SYSTEM_PROMPT_FOR_PLAN)

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
            self.init_plan_messages, f'Напиши план курсовой работы по {self.topic}')

    async def get_plan_response(self):
        response = await client.beta.chat.completions.parse(
            model=self.model,
            messages=self.init_plan_messages,
            response_format=PlanResponse
        )
        self.update_tokens(response)
        plan = response.choices[0].message.content
        self.append_assistant_message(self.init_plan_messages, plan)
        self.plan: PlanResponse = self.plan_parser.parse(plan)
        self.init_body_messages = self.create_system_message(
            COURSE_WORK_BODY_SYSTEM_PROMPT.format(
                topic=self.topic,
                plan=self.plan.model_dump(),
                page_number=self.page_number*3
            )
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

    async def write_chapter(self, chapter_name):
        self.append_user_message(
            self.init_body_messages, f'Напиши текст для раздела "{chapter_name}"')
        response = await client.beta.chat.completions.parse(
            model=self.model,
            messages=self.init_body_messages,
            response_format=ParagraphResponse
        )
        self.update_tokens(response)
        self.append_assistant_message(
            self.init_body_messages, response.choices[0].message.content)

    async def build_course_work(self):
        self.list_of_chapters = self.plan.headings
        for chapter in self.list_of_chapters:
            await self.write_chapter(chapter.heading_text)

        UserActionService.CreateUserAction(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            prompt=self.topic,
            model_open_ai_name=self.model,
            action_type_name=self.action_type_name,
            user_external_id=self.user_external_id
        )
        result_data = self.init_body_messages.copy()
        result_data.pop(0)

        return [
            el['content'][0]['text'].replace(
                'Напиши текст для раздела ', '').replace('"', '')
            if el['role'] == 'user' else self.paragraph_parser.parse(el['content'][0]['text']).paragraphs
            for el in result_data
        ]
