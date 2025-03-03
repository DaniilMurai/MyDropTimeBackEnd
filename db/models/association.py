from sqlalchemy import Table, Column, Integer, ForeignKey
from db.connection import Base

# Промежуточная таблица для связи "многие-ко-многим
product_categories = Table(
    "product_categories",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
)