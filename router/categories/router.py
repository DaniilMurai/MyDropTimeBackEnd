from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from db.depends import get_db
from db.models import Category
from schemas import CategorySchema

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.post("/", response_model=CategorySchema)
def create_category(category_data: CategorySchema, db: Session = Depends(get_db)):
    new_category = Category(category=category_data.category,
                            father_category_id=category_data.father_category_id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.get("/", response_model=list[CategorySchema])
def get_categories(father_category_id: int | None = None, db: Session = Depends(get_db)):
    categories = db.query(Category).filter(Category.father_category_id == father_category_id).all()
    return categories


@router.delete("/{category_id}/",
               response_model=CategorySchema)  # TODO: добавить рекрсивное удаление дочерних категорий
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    db.delete(category)
    db.commit()

    return category
