from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db.connection import Base
from .association  import product_categories

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(500))
    image_url = Column(String(500), nullable=False)
    coupon = Column(String(100))
    type = Column(String(100))
    placement = Column(String(100))

    # Связь с категориями через таблицу product_categories
    categories = relationship("Category", secondary=product_categories, back_populates="products")