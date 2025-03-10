
from Config import (client,
                    PHOTO_MATH_HELPER,
                    PHOTO_MATH_HELPER_PT2,
                    PHOTO_MATH_NEGATIVE_HELPER,
                    )
from DataModels.PhotoMathDataModel import LatexResponse
from langchain.output_parsers import PydanticOutputParser


class SolvePhotoGPTService:
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
            ], max_completion_tokens=10000,
            response_format={
                "type": "text"
            },
            temperature=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        print(f'Всего токенов за запрос: {response.usage.total_tokens}')
        return parser.parse(response.choices[0].message.content)
