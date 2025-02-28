import logging
import os

from fastapi import FastAPI

from router import router

app = FastAPI()

app.include_router(router)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Drop Time API!"}
