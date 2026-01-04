from pydantic import BaseModel
from typing import Optional


class Fighter(BaseModel):
    id: str
    name: str
    image: str  # URL or path to fighter image
    description: Optional[str] = None
