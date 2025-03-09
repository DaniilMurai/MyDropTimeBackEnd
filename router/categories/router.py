from typing import Literal

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


CategorySchema.model_rebuild()


# Функция для рекурсивного получения дерева категорий
def get_category_tree(parent_id: int | None = None, db: Session = Depends(get_db), depth: int = 1) -> list[
    CategorySchema]:
    # Находим категории, у которых father_category_id равен parent_id.
    categories = db.query(Category).filter(Category.father_category_id == parent_id).all()
    result = []
    for category in categories:
        # Если ещё можно спускаться ниже (глубина больше 0), рекурсивно получаем подкатегории.
        subcategories = get_category_tree(category.id, db, depth - 1) if depth > 0 else []
        # Формируем объект схемы с вложенными подкатегориями.
        result.append(CategorySchema(
            id=category.id,
            category=category.category,
            father_category_id=category.father_category_id,
            subcategories=subcategories
        ))
    return result


# Эндпоинт для получения категорий с настройкой глубины вложенности.
@router.get("/", response_model=list[CategorySchema])
def get_categories(
        father_category_id: int | None = None,  # Если None – получаем категории верхнего уровня
        depth: Literal[0, 1, 2] = 1,
        # Глубина рекурсии: 0 – только текущий уровень, 1 – добавить прямые подкатегории, 2 – еще глубже и т.д.
        db: Session = Depends(get_db)
):
    return get_category_tree(father_category_id, db, depth)


@router.put("/{category_id}/", response_model=CategorySchema)
def update_category(category_id: int, category_data: CategorySchema, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(category_id == Category.id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_category.category = category_data.category
    db_category.father_category_id = category_data.father_category_id

    db.commit()
    db.refresh(db_category)

    return db_category


@router.delete("/{category_id}/",
               response_model=CategorySchema)
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
