from fastapi import FastAPI, Depends, HTTPException, Query, File, UploadFile
from fastapi.responses import FileResponse
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db, Product as DBProduct
from pydantic import BaseModel
import logging
import shutil
import os
import cloudinary
import cloudinary.uploader

app = FastAPI()

# Configuration       
cloudinary.config( 
    cloud_name = "ddbkszi8q", 
    api_key = "277472452144523", 
    api_secret = "rs0vTR9lMkZ3tTV2tDo6EiIFH18", # Click 'View API Keys' above to copy your API secret
    secure=True
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Папка для хранения изображений
UPLOAD_DIR = "/opt/render/project/src/static/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Загружаем изображение в Cloudinary и возвращаем ссылку"""
    result = cloudinary.uploader.upload(file.file)
    return {"url": result["secure_url"]}



#Апдейт всех существующих url на картинки
@app.put("/update-image-urls")
def update_image_urls(new_host: str, db: Session = Depends(get_db)):
    products = db.query(DBProduct).all()

    if not products:
        return {"message": "No products found in database"}
    
    for product in products:
        if product.image_url:
            filename = product.image_url.split("/")[-1]
            new_url = f"http://{new_host}/images/{filename}"
            product.image_url = new_url

    db.commit()
    return {"message": "Image URLs updated successfully"}        

# Эндпоинд для получения всех url изображений которые есть в базе на этот момент
@app.get("/images/")
def list_images(db: Session = Depends(get_db)):
    products = db.query(DBProduct.image_url).all()  # Запрашиваем поле image (не image_url)
    image_urls = [product.image_url for product in products]  # Получаем список ссылок
    logger.info("Retrieved images: %s", image_urls)
    return {"images": image_urls}


# Эндпоинт для получения изображений
@app.get("/images/{filename}")
async def get_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path)



# Схема для валидации входных данных
class ProductSchema(BaseModel):
    id: int | None = None  # id теперь необязательное
    name: str
    price: float
    description: str
    image_url: str
    coupon: str
    type: str
    placement: Optional[str] = "default"

class Config:
        orm_mode = True  # Это нужно для преобразования SQLAlchemy объектов в Pydantic модели


#Обновление каритинки
@app.put("/images/{product_id}", response_model=ProductSchema)
def update_image(product_id: int, image_url: str, db: Session = Depends(get_db)):
    db_product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Обновление только image_url
    db_product.image_url = image_url

    # Сохранение изменений
    db.commit()
    db.refresh(db_product)

    # Возвращаем обновленный продукт
    return db_product        


@app.get("/products/placement/{placement}", response_model=List[ProductSchema])
def get_products_by_placement(placement: str, db: Session = Depends(get_db)):
    products = db.query(DBProduct).filter(DBProduct.placement == placement).all()
    return products
       

# Получение всех товаров
from sqlalchemy import desc

@app.get("/products", response_model=List[ProductSchema])
def get_products(
    min_price: float = Query(None, ge=0), 
    max_price: float = Query(None, le=10000), 
    sort_by: str = Query("id", pattern="^(price|id|name|type|placement)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),  # Добавлен параметр для направления сортировки
    placement: str = Query(None, regex="^(News|ComingSoon|TopBar)$"),  # Добавим параметр для фильтрации
    db: Session = Depends(get_db)
):
    logger.info("Received request for products with filters: min_price=%s, max_price=%s, sort_by=%s, sort_order=%s, placement=%s",
                min_price, max_price, sort_by, sort_order, placement)
    
    query = db.query(DBProduct)

    if min_price is not None:
        query = query.filter(DBProduct.price >= min_price)
    if max_price is not None:
        query = query.filter(DBProduct.price <= max_price)

    if placement:
        query = query.filter(DBProduct.placement == placement)  # Фильтруем по placement

    # Определяем поле для сортировки
    sort_field = getattr(DBProduct, sort_by)

    # Применяем направление сортировки
    if sort_order == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    products = query.all()
    
    if not products:
        logger.warning("No products found matching the criteria")
    
    return products




# Получение товара по ID
@app.get("/products/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/products/type/{product_type}", response_model=List[ProductSchema])
def get_products_by_type(product_type: str, db: Session = Depends(get_db)):
    products = db.query(DBProduct).filter(DBProduct.type == product_type).all()
    
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this type")
    
    return products




# Добавление товара
@app.post("/products", response_model=ProductSchema)
def create_product(product: ProductSchema, db: Session = Depends(get_db)):
    # Убедимся, что поле image_url не пустое
    if not product.image_url:
        raise HTTPException(status_code=400, detail="Image URL must be provided")

    # Мы не указываем id, оно будет сгенерировано автоматически
    db_product = DBProduct(**product.dict(exclude={'id'}))  # Исключаем id
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product




# Обновление товара
@app.put("/products/{product_id}", response_model=ProductSchema)
def update_product(product_id: int, product: ProductSchema, db: Session = Depends(get_db)):
    db_product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
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

@app.delete("/products/{product_id}", response_model=ProductSchema)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()

    return db_product




@app.get("/")
def read_root():
    return {"message": "Welcome to the Drop Time API!"}

