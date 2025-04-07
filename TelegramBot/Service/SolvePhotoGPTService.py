
from Config import (client,
                    PHOTO_MATH_HELPER,
                    AI_MODELS
                    )
from DataModels.PhotoMathDataModel import LatexResponse
from langchain.output_parsers import PydanticOutputParser
from .UserActionService import UserActionService
from openai.types import Completion


class SolvePhotoGPTService:
    def __init__(self, external_id):
        self.user_external_id = external_id
        self.model = AI_MODELS.GPT_4_O_MINI_2024_07_18
        self.parser = PydanticOutputParser(pydantic_object=LatexResponse)
        self.action_type_name = 'photo_issue_helper'
        self.messages = [
            {
                "role": "system",
                "content": [
                        {
                            "type": "text",
                            "text": PHOTO_MATH_HELPER + str(self.parser.get_format_instructions())
                        }
                ]
            },
        ]

    def add_message(self, caption, base64_image):
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
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                            }
                ]
            }
        )

    def add_action(self, response: Completion, ):
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

    async def generate_response(self,):
        response = await client.beta.chat.completions.parse(
            model=self.model.value,
            messages=self.messages,
            max_completion_tokens=10000,
            response_format=LatexResponse,
        )
        self.add_action(response)
        return self.parser.parse(response.choices[0].message.content)
