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
        return parser.parse(response.choices[0].message.content)
