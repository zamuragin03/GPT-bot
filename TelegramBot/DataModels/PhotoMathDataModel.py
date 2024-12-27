from typing import List
from pydantic import BaseModel, Field

class LatexResponse(BaseModel):
    code: str = Field(description="Step-by-step ready-made code of solution written in LaTeX")

