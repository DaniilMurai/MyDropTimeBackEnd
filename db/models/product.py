from sqlalchemy import Column, Float, Integer, String

from db.connection import Base


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
