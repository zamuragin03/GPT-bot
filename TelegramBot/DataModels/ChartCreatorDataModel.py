from typing import List
from pydantic import BaseModel, Field


class ChartResponse(BaseModel):
    x_range: str = Field(description="range of x values in python code for matplotlib chart")
    y_range: str = Field(description="range of y values in python code for matplotlib chart")
    title: str = Field(description="title of user's request function")
    leave: bool = Field(description="True, if user trying to crash the interface, False, if user request id adequate")
    