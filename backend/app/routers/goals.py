# backend/app/routers/goals.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter(
    prefix="/goals",
    tags=["goals"]
)

# (НОВЫЙ ЭНДПОИНТ)
@router.put("/{tracker_id}", response_model=schemas.GoalTrackerRead)
def update_goal_tracker_settings(
    tracker_id: int,
    tracker_data: schemas.GoalTrackerUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Обновляет настройки существующей цели (целевое значение, тип и т.д.).
    """
    db_tracker = crud.get_goal_tracker(db, tracker_id=tracker_id)
    if not db_tracker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal tracker not found")

    # Проверка прав: убедиться, что пользователь владеет списком
    if db_tracker.item.list.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    return crud.update_goal_tracker(db=db, db_tracker=db_tracker, tracker_data=tracker_data)

@router.post("/{tracker_id}/log", response_model=schemas.GoalTrackerRead)
def log_goal_progress(
    tracker_id: int,
    log_data: schemas.GoalLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Записывает прогресс для отслеживаемой цели.
    """
    # 1. Найти в базе GoalTracker
    db_tracker = crud.get_goal_tracker(db, tracker_id=tracker_id)
    if not db_tracker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal tracker not found")

    # 2. Проверка прав доступа: убедиться, что пользователь владеет списком
    if db_tracker.item.list.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to log progress for this goal")

    # 3. Создать новую запись в таблице GoalLog
    db_log = models.GoalLog(
        tracker_id=db_tracker.id,
        value_added=log_data.value
    )
    db.add(db_log)

    # 4. Обновить поле current_value в трекере
    db_tracker.current_value += log_data.value
    
    # (ИЗМЕНЕНИЕ) Добавляем защиту от отрицательного прогресса
    if db_tracker.current_value < 0:
        db_tracker.current_value = 0

    # 5 & 6. Проверить, выполнена ли цель и обновить связанный Item
    is_completed = False
    if db_tracker.goal_type == models.GoalType.CUMULATIVE:
        if db_tracker.target_value is not None and db_tracker.current_value >= db_tracker.target_value:
            is_completed = True
    elif db_tracker.goal_type == models.GoalType.CHECK_IN:
        if db_tracker.target_count is not None and db_tracker.current_value >= db_tracker.target_count:
            is_completed = True
    
    if is_completed and not db_tracker.item.is_completed:
        db_tracker.item.is_completed = True

    # 7. Сохранить все изменения в базе
    db.commit()
    db.refresh(db_tracker)

    # 8. Вернуть обновленный трекер
    return db_tracker