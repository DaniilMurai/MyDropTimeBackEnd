import os

import cloudinary
import cloudinary.api
import cloudinary.uploader
from fastapi import APIRouter, File, UploadFile

router = APIRouter(
    prefix="/cloudinary",
    tags=["cloudinary"]
)

# Configuration
cloudinary.config(
    cloud_name="ddbkszi8q",
    api_key="277472452144523",
    api_secret="rs0vTR9lMkZ3tTV2tDo6EiIFH18",  # Click 'View API Keys' above to copy your API secret
    secure=True,
)


@router.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):

    """Загружаем несколько изображений в Cloudinary и возвращаем ссылки без версии"""
    uploaded_urls = [] 

    for file in files:
        original_filename = os.path.splitext(file.filename)[0]  # Убираем расширение
        result = cloudinary.uploader.upload(
            file.file,
            public_id=original_filename,  # Фиксированное имя файла
            unique_filename=False,  # Отключаем случайные имена
            overwrite=True  # Разрешаем перезапись
        )

        # Убираем версию из ссылки
        clean_url = result["secure_url"].replace(f"/v{result['version']}/", "/")
        uploaded_urls.append(clean_url)

    return {"urls": uploaded_urls}



@router.get("/images/")
async def list_cloudinary_images(next_cursor: str = None):
    """Получает все ссылки на изображения из Cloudinary с постраничным запросом"""
    try:
        params = {"type": "upload", "max_results": 100}
        if next_cursor:
            params["next_cursor"] = next_cursor

        response = cloudinary.api.resources(**params)
        image_urls = [item["secure_url"] for item in response["resources"]]

        return {
            "images": image_urls,
            "next_cursor": response.get("next_cursor")  # Для следующей страницы
        }
    except Exception as e:
        return {"error": str(e)}
