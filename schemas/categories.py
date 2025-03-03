

from pydantic import BaseModel

class CategorySchema(BaseModel):
    category: str
    father_category_id: int | None = None