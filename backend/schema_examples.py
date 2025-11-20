from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional

# Examples only to guide future collections

class Product(BaseModel):
    id: Optional[str] = Field(default=None)
    title: str
    price: float


class Post(BaseModel):
    id: Optional[str] = Field(default=None)
    title: str
    body: str
