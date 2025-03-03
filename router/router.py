from fastapi import APIRouter

from . import cloudinary_, products, categories

router = APIRouter()

router.include_router(products.router)
router.include_router(cloudinary_.router)
router.include_router(categories.router())