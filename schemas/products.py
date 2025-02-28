from typing import Literal, Optional

from pydantic import BaseModel

ProductType = Literal["protein", "mix", "creatine"]
ProductPlacement = Literal["TopBar", "News", "ComingSoon"]


class ProductSchema(BaseModel):
    id: int | None = None  # id теперь необязательное
    name: str
    price: float
    description: str
    image_url: str
    coupon: str
    type: ProductType
    placement: Optional[ProductPlacement] = "default"
