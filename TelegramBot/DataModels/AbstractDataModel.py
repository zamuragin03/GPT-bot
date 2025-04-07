from typing import List
from pydantic import BaseModel, Field




class HeadingObject(BaseModel):
    heading_text: str = Field(
        description="Heading text to be used in the future pptx presentation file; examples=['<h1>Heading 1</h1>', '<h2>Heading 2</h2>']",)

class PlanResponse(BaseModel):
    headings: List[HeadingObject] = Field(
        description="List of headings to be used in the future abstract work")

class ParagraphResponse(BaseModel):
    paragraphs: list[str] = Field(description="List of paragraphs to be used in the future abstract work; examples=['<p>Paragraph 1</p>', '<p>Paragraph 2</p>']",)
