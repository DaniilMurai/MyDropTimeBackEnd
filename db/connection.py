# Получаем URL базы из Render
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "postgresql://mydatabase_iav7_user:R1c8xIhJI9qswKQsyZdyujYDYS0dKP2r@dpg-cuvj313tq21c73btr2v0-a.oregon-postgres.render.com/mydatabase_iav7"
    # raise ValueError("ERROR: Переменная окружения DATABASE_URL не задана!")


# Render использует "postgres://" вместо "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://") + "?sslmode=require"

# Создаём подключение
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
