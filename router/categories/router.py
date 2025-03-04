from fastapi import APIRouter, HTTPException
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


@router.put("/{category_id}/", response_model=CategorySchema)
def update_category(category_id: int, category_data: CategorySchema, db: Session = Depends(get_db())):
    db_category = db.query(Category).filter(category_id == Category.id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_category.category = category_data.category
    db_category.father_category_id = category_data.father_category_id

    db.commit()
    db.refresh(db_category)

    return db_category


@router.delete("/{category_id}/",
               response_model=CategorySchema)  # TODO: добавить рекрсивное удаление дочерних категорий
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    print(f"🛑 Удаляем категорию: {category.category} (ID={category_id})")

    #  Получаем все подкатегории
    subcategories = db.query(Category).filter(Category.father_category_id == category_id).all()

    #  Рекурсивно удаляем все подкатегории
    for subcategory in subcategories:
        print(f"🔄 Удаляем подкатегорию: {subcategory.category} (ID={subcategory.id})")
        delete_category(subcategory.id, db)  # Рекурсивный вызов!

    db.delete(category)
    db.commit()

    print(f"✅ Категория {category.category} (ID={category_id}) удалена.")
    return {"message": f"Category {category.category} and all subcategories deleted"}
