from typing import List
from pydantic import BaseModel, Field


class SlideObject(BaseModel):
    slide_index: int = Field(
        description="slide index in future pptx presentation file")
    slide_title: str = Field(description='Presentation slide title')
    slide_description: str = Field(
        description='Presentation slide description')
    photo_query: str = Field(
        description="Qurey param for unsplash api image search")


class PowerPointResponseObject(BaseModel):
    pages: List[SlideObject]


class SlideObjectWithPhoto(BaseModel):
    slide_index: int = Field(
        description="slide index in future pptx presentation file")
    slide_title: str = Field(description='Presentation slide title')
    slide_description: str = Field(
        description='Presentation slide description')
    photo_url: str = Field(
        description="Link to image")


class PowerPointFinalObject(BaseModel):
    pages: List[SlideObjectWithPhoto]


class VBACodeResult(BaseModel):
    code: str = Field(
        description='ready-made code written in vba for power point')
