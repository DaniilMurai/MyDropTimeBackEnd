from pydantic import BaseModel


class CategorySchema(BaseModel):
    id: int | None = None
    category: str
    father_category_id: int | None = None
