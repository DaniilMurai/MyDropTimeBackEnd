

from pydantic import BaseModel

class CategorySchema(BaseModel):
    category: str
    sub_category: str | None = None