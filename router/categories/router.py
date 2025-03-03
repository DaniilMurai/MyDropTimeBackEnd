from http.client import responses, HTTPException

from fastapi import APIRouter, File, UploadFile
import os

from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from unicodedata import category

from db import Product
from db.models import Category
from db.depends import get_db
from schemas import CategorySchema

router = APIRouter(
    prefix= "/categories",
    tags = ["categories"],
)


@router.post("/", response_model=CategorySchema)
def create_category(category_data: CategorySchema, db: Session = Depends(get_db)):
    new_category = Category(category = category_data.category,
                            sub_category = category_data.sub_category)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/", response_model= list[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

@router.get("/{category_id}/products", response_model= list[dict])
def get_products_by_category(category_id: int, db:Session = Depends(get_db)):
    # Получаем категорию по id
    category_ = db.query(Category).filter(Category.id == category_id).first()
    if not category_:
        raise HTTPException(status_code=404, detail="Category not found")

    products = category_.products

    if not products:
        raise HTTPException(status_code=404, detail="No products found in this category")

    return [{"id": p.id, "name": p.name, "price": p.price, "image_url": p.image_url} for p in products]

