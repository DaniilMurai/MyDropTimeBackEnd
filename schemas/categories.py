from pydantic import BaseModel


class CategorySchema(BaseModel):
    id: int | None = None
    category: str
    father_category_id: int | None = None
    subcategories: list["CategorySchema"] = []  # Рекурсивное поле для вложенных категорий

    class Config:
        orm_mode = True
