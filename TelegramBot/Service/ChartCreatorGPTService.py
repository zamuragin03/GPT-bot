from openai.types import Completion
from Config import (client,
                    CHART_CREATOR_PROMPT,

                    )
from .UserActionService import UserActionService
from DataModels.ChartCreatorDataModel import *
from langchain.output_parsers import PydanticOutputParser


class ChartCreatorGPTService:
    def __init__(self, external_id):
        self.user_external_id = external_id
        self.model = "gpt-4o"
        self.parser = PydanticOutputParser(pydantic_object=ChartResponse)
        self.messages = [
            {
                "role": "system",
                "content": [
                        {
                            "type": "text",
                            "text": CHART_CREATOR_PROMPT.format(format_instructions=self.parser.get_format_instructions())

                        }
                ]
            },
        ]
        self.action_type_name = 'chart_creator_helper'

    def add_action(self, response: Completion, ):
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

    def add_message(self, message: str):
        self.messages.append({
            "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message
                        },
                    ]
        })

    async def GetChartCode(self):
        response = await client.beta.chat.completions.parse(
            model=self.model,
            messages=self.messages,
            response_format=ChartResponse
        )
        self.add_action(response)
        return self.parser.parse(response.choices[0].message.content)
