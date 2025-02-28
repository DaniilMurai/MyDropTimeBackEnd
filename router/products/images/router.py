import logging
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from config import UPLOAD_DIR
from database import Product, get_db
from schemas import ProductSchema

router = APIRouter(
    prefix="/images",
)

logger = logging.getLogger(__name__)


# Эндпоинд для получения всех url изображений которые есть в базе на этот момент
@router.get("/")
def list_images(db: Session = Depends(get_db)):
    products = db.query(Product.image_url).all()  # Запрашиваем поле image (не image_url)
    image_urls = [product.image_url for product in products]  # Получаем список ссылок
    logger.info("Retrieved images: %s", image_urls)
    return {"images": image_urls}


# Эндпоинт для получения изображений
@router.get("/{filename}")
async def get_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path)


# Обновление каритинки
@router.put("/{product_id}", response_model=ProductSchema)
def update_image(product_id: int, image_url: str, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()

    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Обновление только image_url
    db_product.image_url = image_url

    # Сохранение изменений
    db.commit()
    db.refresh(db_product)

    # Возвращаем обновленный продукт
    return db_product
