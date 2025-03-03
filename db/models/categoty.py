from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db.connection import Base
from .association import product_categories

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key = True, index = True, autoincrement=True)
    category = Column(String(255), nullable=False)
    father_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # Родительская категория


    products = relationship("Product", secondary=product_categories, back_populates="categories")
    # Отношения для вложенных категорий
    parent = relationship("Category", remote_side=[id], backref="subcategories")