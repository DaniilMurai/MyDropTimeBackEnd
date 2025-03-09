from pydantic import BaseModel


class ProductWithCategorySchema(BaseModel):
    product_id: int
    product_name: str
    category_id: int
    category_name: str
