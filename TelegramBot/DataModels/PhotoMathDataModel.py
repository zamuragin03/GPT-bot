from typing import List
from pydantic import BaseModel, Field

class LatexResponse(BaseModel):
    code: List[str] = Field(description="list of Step-by-step ready-made code of solution written in LaTeX. example: ['\\frac{1}{2} + \\frac{1}{3} = \\frac{3}{6} + \\frac{2}{6} = \\frac{5}{6}', '\\frac{5}{6} = 0.8333']")
