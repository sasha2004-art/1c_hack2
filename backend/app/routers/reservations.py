from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter(
    prefix="/items/{item_id}",
    tags=["reservations"]
)

@router.post("/reserve", response_model=schemas.ReservationRead, status_code=status.HTTP_201_CREATED)
def reserve_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Забронировать элемент в вишлисте."""
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    
    # Проверка 1: Элемент должен быть в списке типа "wishlist"
    if db_item.list.list_type != models.ListType.WISHLIST:
        raise HTTPException(status_code=400, detail="Бронировать можно только элементы из вишлистов")

    # Проверка 2: Пользователь не может бронировать свои собственные желания
    if db_item.list.owner_id == current_user.id:
        raise HTTPException(status_code=403, detail="Вы не можете бронировать свои собственные желания")

    # Проверка 3: Элемент не должен быть уже забронирован
    existing_reservation = crud.get_reservation_by_item_id(db, item_id=item_id)
    if existing_reservation:
        raise HTTPException(status_code=409, detail="Этот элемент уже забронирован")
        
    return crud.create_reservation(db=db, item=db_item, user=current_user)


@router.delete("/unreserve", response_model=schemas.ReservationRead)
def unreserve_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Снять бронь с элемента."""
    db_reservation = crud.get_reservation_by_item_id(db, item_id=item_id)
    
    if not db_reservation:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    
    # Проверка: только пользователь, который забронировал элемент, может снять бронь
    if db_reservation.reserver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Вы не можете снять чужое бронирование")
        
    # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
    # 1. Создаем Pydantic-модель для ответа ДО удаления объекта из БД.
    #    response_data теперь является безопасной копией данных.
    response_data = schemas.ReservationRead.from_orm(db_reservation)
    
    # 2. Вызываем функцию удаления, но ее результат нам больше не нужен.
    crud.delete_reservation(db=db, db_reservation=db_reservation)
    
    # 3. Возвращаем безопасную копию данных. FastAPI легко превратит ее в JSON.
    return response_data