from typing import Optional

from pydantic import BaseModel


class ProductSchema(BaseModel):
    id: int | None = None  # id теперь необязательное
    name: str
    price: float
    description: str
    image_url: str
    coupon: str
    type: str
    placement: Optional[str] = "default"
