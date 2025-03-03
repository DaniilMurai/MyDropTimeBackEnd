from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from db.connection import Base
from .association import product_categories

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key = True, index = True, autoincrement=True)
    category = Column(String(255)) #nullable = false
    sub_category = Column(String(255)) #nullable = false

    # Связь с продуктами через таблицу product_categories
    products = relationship("Product", secondary=product_categories, back_populates="categories")
