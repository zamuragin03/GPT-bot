from Config import (
    OPENAI_TOKEN,
    REWRITING_STYSTEM_PROMPT,
)
from .UserActionService import UserActionService
from langchain_core.messages import BaseMessage
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI


class RewritingGPTService:
    def __init__(self, external_id):
        self.external_id = external_id
        self.model_name = "gpt-4o"
        self.action_type_name = 'rewriting_helper'
        self.messages = [SystemMessage(content=REWRITING_STYSTEM_PROMPT)]
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
        self.messages = [SystemMessage(content=REWRITING_STYSTEM_PROMPT)]

    async def generate_response(self, message):
        self.messages.append(HumanMessage(content=message))
        result = await self.model.ainvoke(self.messages.copy())
        response = result.content
        self.messages.append(AIMessage(content=response))
        self.add_action(result, message)
        return response
