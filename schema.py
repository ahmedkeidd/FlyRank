from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Category(str, Enum):
    fiction = "fiction"
    nonfiction = "nonfiction"
    poetry = "poetry"
    childrens = "childrens"
    other = "other"

class QualityFlag(str, Enum):
    missing_description = "missing_description"
    short_description = "short_description"
    generic_title = "generic_title"

class EnrichInput(BaseModel):
    title: str
    description: Optional[str] = None

class EnrichOutput(BaseModel):
    category: Category
    summary: str
    quality_flags: List[QualityFlag] = []