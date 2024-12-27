import re
import httpx
import asyncio
from openai.types import Completion
from Config import (client, CODE_HELPER_SYSTEM_PROMPT,
                    OPENAI_TOKEN,
                    PRESENTATION_HELPER_SYSTEM_PROMPT,
                    PRESENTATION_HELPER_USER_PROMPT,
                    PRESENTATION_HELPER_USER_FINAL_PROMPT,
                    PHOTO_MATH_HELPER,
                    PHOTO_MATH_HELPER_PT2,
                    PHOTO_MATH_NEGATIVE_HELPER,
                    CHART_CREATOR_PROMPT,
                    DEFAULT_MODE_SYSTEM_PROMPT,
                    ABSTRACT_WRITER_SYSYTEM_PROMPT,
                    COURSE_WORK_SYSTEM_PROMPT_FOR_PLAN,
                    COURSE_WORK_BODY_SYSTEM_PROMPT
                    )
from .BotService import BotService
from .UnsplashService import UnsplashService
from .UserActionService import UserActionService
from DataModels.PowerPointDataModel import *
from DataModels.PhotoMathDataModel import *
from DataModels.ChartCreatorDataModel import *
from langchain_core.messages import BaseMessage
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage, FunctionMessage
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser


class ChatGPTService:
    async def SolvePhotoProblem(caption, base64_image):
        parser = PydanticOutputParser(pydantic_object=LatexResponse)
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": PHOTO_MATH_HELPER.format(format_instructions=parser.get_format_instructions())
                            + PHOTO_MATH_HELPER_PT2 + PHOTO_MATH_NEGATIVE_HELPER
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": caption
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        }
                    ]
                }
            ], max_completion_tokens=10000
        )
        print(f'Всего токенов за запрос: {response.usage.total_tokens}')
        return parser.parse(response.choices[0].message.content)


class CodeHelperGPTService:
    def __init__(self, external_id):
        self.external_id = external_id
        self.model_name = "gpt-4-turbo"
        self.action_type_name = 'code_helper'
        self.messages = [SystemMessage(content=CODE_HELPER_SYSTEM_PROMPT)]
        self.model = ChatOpenAI(model=self.model_name, api_key=OPENAI_TOKEN)

    def add_action(self, response: BaseMessage, user_request: str):
        UserActionService.CreateUserAction(
            input_tokens=response.response_metadata.get(
                'token_usage').get('prompt_tokens'),
            output_tokens=response.response_metadata.get(
                'token_usage').get('completion_tokens'),
            prompt=user_request,
            model_open_ai_name=self.model_name,
            action_type_name=self.action_type_name,
            user_external_id=self.external_id
        )

    def clear_context(self):
        self.messages = [SystemMessage(content=CODE_HELPER_SYSTEM_PROMPT)]

    async def generate_response(self, message):
        self.messages.append(HumanMessage(content=message))
        result = await self.model.ainvoke(self.messages.copy())
        response = result.content
        self.messages.append(AIMessage(content=response))
        self.add_action(result, message)
        return response


# class PhotoMathGPT:
#     def __init__(self):
#         self.messages = [SystemMessage(content=CODE_HELPER_SYSTEM_PROMPT)]
#         self.model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_TOKEN)

#     def clear_context(self):
#         self.messages = [SystemMessage(content=CODE_HELPER_SYSTEM_PROMPT)]

#     async def generate_response(self, message):
#         self.messages.append(HumanMessage(content=message))
#         result = await self.model.ainvoke(self.messages.copy())
#         response = result.content
#         self.messages.append(AIMessage(content=response))
#         return response


class PowerPointHelperGPTService:
    def __init__(self, slides_count, topic, presentation_style):
        self.init_messages = [
            ('system', PRESENTATION_HELPER_SYSTEM_PROMPT),
            ('human', PRESENTATION_HELPER_USER_PROMPT),
        ]
        self.model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_TOKEN)

        prompt_template = ChatPromptTemplate(self.init_messages.copy())
        self.parser = PydanticOutputParser(
            pydantic_object=PowerPointResponseObject)
        self.prompt = prompt_template.invoke({
            'slides_count': slides_count,
            "topic": topic,
            "presentation_style": presentation_style,
            'format_instructions': self.parser.get_format_instructions()
        })

    async def prepare_skelet(self):
        response = await self.model.ainvoke(self.prompt)
        self.skelet = self.parser.parse(response.content)

    def get_filled_images(self,):
        skelet_with_photos = []
        for page in self.skelet.pages:
            photo_url = UnsplashService.GetImageLinkByParam(page.photo_query)
            skelet_with_photos.append(SlideObjectWithPhoto(slide_index=page.slide_index,
                                                           slide_title=page.slide_title,
                                                           slide_description=page.slide_description,
                                                           photo_url=photo_url))

        return PowerPointFinalObject(pages=skelet_with_photos)

    async def Get_Presentation_Code(self):

        # Надо правильно обновить список сообщений, вставить туда tool, и после этого вызвать финальный промпт
        filled_message = self.get_filled_images()
        self.prompt.append(FunctionMessage(filled_message))
        prompt_template = ChatPromptTemplate(
            PRESENTATION_HELPER_USER_FINAL_PROMPT)
        self.final_parser = PydanticOutputParser(
            pydantic_object=VBACodeResult)
        prompt = prompt_template.invoke(
            {'format_instructions': self.final_parser.get_format_instructions()})
        self.prompt.append(prompt)
        response = await self.model.ainvoke(self.messages)
        return self.final_parser.parse(response.content)


class ChartCreatorGPTService:
    def __init__(self, external_id):
        self.user_external_id = external_id
        self.model = "gpt-4o-mini"
        self.action_type_name = 'chart_creator_helper'

    def add_action(self, response: Completion, user_request: str):
        UserActionService.CreateUserAction(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            prompt=user_request,
            model_open_ai_name=self.model,
            action_type_name=self.action_type_name,
            user_external_id=self.user_external_id
        )

    async def GetChartCode(self, user_request):
        parser = PydanticOutputParser(pydantic_object=ChartResponse)
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": CHART_CREATOR_PROMPT.format(format_instructions=parser.get_format_instructions())

                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_request
                        },
                    ]
                }
            ]
        )
        self.add_action(response, user_request)
        print(parser.parse(response.choices[0].message.content))
        return parser.parse(response.choices[0].message.content)


class DefaultModeGPTService:
    def __init__(self, external_id):
        self.user_external_id = external_id
        self.model = "gpt-4o-mini"
        self.action_type_name = 'default_mode'
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
            },
        )

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

    def add_action(self, response: Completion):
        last_message = list(filter(lambda x: x.get(
            'role') == 'user', self.messages))[-1].get('content')[0].get('text')
        UserActionService.CreateUserAction(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            prompt=last_message,
            model_open_ai_name=self.model,
            action_type_name=self.action_type_name,
            user_external_id=self.user_external_id
        )

    async def generate_response(self):
        response = await client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        self.add_action(response)
        return response.choices[0].message.content


class AbstractWriterGPTService:
    def __init__(self, topic, external_id):
        self.user_external_id = external_id
        self.topic = topic
        self.model = "gpt-4o"
        self.action_type_name = 'abstract_writer'
        self.input_tokens = 0
        self.output_tokens = 0
        self.messages = [
            {
                "role": "system",
                "content": [
                        {
                            "type": "text",
                            "text": ABSTRACT_WRITER_SYSYTEM_PROMPT.format(topic=self.topic)
                        }
                ]
            },
        ]

    def add_message(self, content, role="user" or "assistant"):
        self.messages.append(
            {
                "role": role,
                "content": [
                    {
                        "type": "text",
                        "text": content
                    }
                ]
            },
        )

    async def write_introduction(self,):
        self.add_message(
            content='Напиши введение для данной работы', role="user")
        response = await client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        self.input_tokens += response.usage.prompt_tokens
        self.output_tokens += response.usage.completion_tokens
        self.add_message(response.choices[0].message.content, role='assistant')

    async def write_body(self,):
        self.add_message(
            content='Напиши основную часть для данной работы', role="user")
        response = await client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        self.input_tokens += response.usage.prompt_tokens
        self.output_tokens += response.usage.completion_tokens
        self.add_message(response.choices[0].message.content, role='assistant')

    async def write_conclustion(self,):
        self.add_message(
            content='Напиши заключение для данной работы', role="user")
        response = await client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        self.input_tokens += response.usage.prompt_tokens
        self.output_tokens += response.usage.completion_tokens
        self.add_message(response.choices[0].message.content, role='assistant')

    async def write_literature_list(self,):
        self.add_message(
            content='Напиши cписок используемой литературы для данной работы', role="user")
        response = await client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        self.input_tokens += response.usage.prompt_tokens
        self.output_tokens += response.usage.completion_tokens
        self.add_message(response.choices[0].message.content, role='assistant')

    async def get_abstract(self,):
        await self.write_introduction()
        await self.write_body()
        await self.write_conclustion()
        await self.write_literature_list()
        UserActionService.CreateUserAction(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            prompt=self.topic,
            model_open_ai_name=self.model,
            action_type_name=self.action_type_name,
            user_external_id=self.user_external_id
        )
        return list(filter(lambda x: x.get('role') == 'assistant', self.messages))


class CourseWorkGPTService:
    def __init__(self, external_id, topic):
        self.user_external_id = external_id
        self.model = "gpt-4o"
        self.action_type_name = 'course_work_helper'
        self.input_tokens = 0
        self.output_tokens = 0
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
        response = await client.chat.completions.create(
            model=self.model,
            messages=self.init_plan_messages
        )
        self.update_tokens(response)

        plan = response.choices[0].message.content
        self.append_assistant_message(self.init_plan_messages, plan)
        self.plan = plan
        self.init_body_messages = self.create_system_message(
            COURSE_WORK_BODY_SYSTEM_PROMPT.format(
                topic=self.topic, plan=self.plan)
        )
        return self.plan

    def regenerate_plan(self):
        self.append_user_message(
            self.init_plan_messages, 'Сгенерируй другой план')

    def regenerate_plan_with_user_detail(self, user_message):
        self.append_user_message(
            self.init_plan_messages, f'Сгенерируй другой план с учетом пожелания пользователя:{user_message}. Если считаешь пожелание пользователя неадекватным, то просто сгенерируй новый план')

    @staticmethod
    def extract_headers(text):
        headers_pattern = re.compile(r"(<h[12]>.*?<\/h[12]>)")
        headers = headers_pattern.findall(text)
        return headers

    async def write_chapter(self, chapter_name):
        self.append_user_message(
            self.init_body_messages, f'Напиши текст для раздела "{chapter_name}"')
        response = await client.chat.completions.create(
            model=self.model,
            messages=self.init_body_messages
        )
        self.update_tokens(response)
        self.append_assistant_message(
            self.init_body_messages, response.choices[0].message.content)

    async def build_course_work(self):
        self.list_of_chapters = CourseWorkGPTService.extract_headers(self.plan)
        for chapter in self.list_of_chapters:
            await self.write_chapter(chapter)
            await asyncio.sleep(10)
        UserActionService.CreateUserAction(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            prompt=self.topic,
            model_open_ai_name=self.model,
            action_type_name=self.action_type_name,
            user_external_id=self.user_external_id
        )
        return list(filter(lambda x: x.get('role') == 'assistant', self.init_body_messages))
    
    async def build_course_work_mock(self):
        await asyncio.sleep(16)
        return 123
    
