import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from db.depends import get_db
from db.models import Product
from schemas import ProductPlacement, ProductSchema, ProductType, CategorySchema
from .images import router as images_router

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

logger = logging.getLogger(__name__)


@router.get("/", response_model=list[ProductSchema])
def get_products(category_id: int | None = None,
                 min_price: float = Query(None, ge=0),
                 max_price: float = Query(None, le=10000),
                 sort_by: Literal["price", "id", "name", "type", "placement"] = Query("id"),
                 # Добавлен параметр для направления сортировки
                 sort_order: Literal["asc", "desc"] = Query("desc"),
                 placement: ProductPlacement = Query(None),  # Добавим параметр для
                 # фильтрации
                 db: Session = Depends(get_db)
                 ):
    logger.info(
        "Received request for products with filters: min_price=%s, max_price=%s, sort_by=%s, sort_order=%s, placement=%s",
        min_price, max_price, sort_by, sort_order, placement
    )

    query = db.query(Product)
    if category_id:
        query = query.filter(Product.categories.any(id=category_id))

    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if placement:
        query = query.filter(Product.placement == placement)  # Фильтруем по placement

    # Определяем поле для сортировки
    sort_field = getattr(Product, sort_by)

    # Применяем направление сортировки
    if sort_order == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    products = query.all()

    if not products:
        logger.warning("No products found matching the criteria")

    return products


# Добавление товара
@router.post("/", response_model=ProductSchema)
def create_product(product: ProductSchema, db: Session = Depends(get_db)):
    # Убедимся, что поле image_url не пустое
    if not product.image_url:
        raise HTTPException(status_code=400, detail="Image URL must be provided")

    # Мы не указываем id, оно будет сгенерировано автоматически
    db_product = Product(**product.model_dump(exclude={'id'}))  # Исключаем id
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/placement/{placement}", response_model=list[ProductSchema])
def get_products_by_placement(placement: ProductPlacement, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.placement == placement).all()
    return products


# TODO удалить хуйню метод, но перед этим поменть во фронте обращение на просто get_products
@router.get("/type/{product_type}", response_model=list[ProductSchema])
def get_products_by_type(product_type: ProductType, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.type == product_type).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found for this type")

    return products


# Получение товара по ID
@router.get("/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Обновление товара
@router.put("/{product_id}", response_model=ProductSchema)
def update_product(product_id: int, product: ProductSchema, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Обновляем данные товара
    db_product.name = product.name
    db_product.price = product.price
    db_product.description = product.description
    db_product.image_url = product.image_url
    db_product.coupon = product.coupon
    db_product.placement = product.placement

    db.commit()
    db.refresh(db_product)

    return db_product


@router.delete("/{product_id}", response_model=ProductSchema)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()

    return db_product


# 📌 Получить все категории для продукта
@router.get("/{product_id}/categories", response_model=list[CategorySchema])
def get_categories_by_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Извлекаем все категории, связанные с этим продуктом через промежуточную таблицу
    categories = product.categories
    return [{"category": c.category, "sub_category": c.sub_category} for c in categories]


# Апдейт всех существующих url на картинки
@router.put("/update-image-urls")
def update_image_urls(new_host: str, db: Session = Depends(get_db)):
    products = db.query(Product).all()

    if not products:
        return {"message": "No products found in database"}

    for product in products:
        if product.image_url:
            filename = product.image_url.split("/")[-1]
            new_url = f"http://{new_host}/{filename}"
            product.image_url = new_url

    db.commit()
    return {"message": "Image URLs updated successfully"}


router.include_router(images_router)
