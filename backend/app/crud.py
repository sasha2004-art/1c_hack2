from typing import List as TypingList, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from . import models, schemas, security

# Define default list title for copied items
DEFAULT_COPY_LIST_TITLE = "Мои сохраненные элементы" 


# --- CRUD для Пользователей ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# --- НОВАЯ ФУНКЦИЯ ДЛЯ ВХОДА ---
def get_user_by_email_or_name(db: Session, login_identifier: str) -> Optional[models.User]:
    """Ищет пользователя по email ИЛИ по имени."""
    return db.query(models.User).filter(
        or_(
            models.User.email == login_identifier,
            models.User.name == login_identifier
        )
    ).first()

# --- ИЗМЕНИТЬ ЭТУ ФУНКЦИЮ ---
def search_users_by_email(db: Session, query: str, current_user_id: int, limit: int = 10):
    """Ищет пользователей по частичному совпадению email ИЛИ имени, исключая текущего пользователя."""
    return db.query(models.User).filter(
        or_(
            models.User.email.ilike(f"%{query}%"),
            models.User.name.ilike(f"%{query}%")
        ),
        models.User.id != current_user_id
    ).limit(limit).all()

# --- ИЗМЕНИТЬ ЭТУ ФУНКЦИЮ ---
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    # Добавляем user.name при создании
    db_user = models.User(email=user.email, name=user.name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- (Задача 4.1) CRUD для Друзей ---

def get_friendship_request(db: Session, request_id: int) -> Optional[models.Friendship]:
    """Получить заявку в друзья по ее ID."""
    return db.query(models.Friendship).filter(models.Friendship.id == request_id).first()

def get_existing_friendship(db: Session, user1_id: int, user2_id: int) -> Optional[models.Friendship]:
    """Проверить, существует ли какая-либо связь (заявка или дружба) между двумя пользователями."""
    return db.query(models.Friendship).filter(
        or_(
            (models.Friendship.requester_id == user1_id) & (models.Friendship.addressee_id == user2_id),
            (models.Friendship.requester_id == user2_id) & (models.Friendship.addressee_id == user1_id)
        )
    ).first()

def create_friend_request(db: Session, requester_id: int, addressee_id: int) -> models.Friendship:
    """Создать новую заявку в друзья."""
    db_request = models.Friendship(requester_id=requester_id, addressee_id=addressee_id, status=models.FriendshipStatus.PENDING)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Создаем уведомление для получателя
    create_notification(
        db,
        recipient_id=addressee_id,
        sender_id=requester_id,
        type=models.NotificationType.FRIEND_REQUEST
    )
    # Перезагружаем объект, чтобы подгрузить связь с уведомлением
    db.refresh(db_request, attribute_names=['addressee'])
    
    return db_request # <-- Возвращаем объект Friendship

def update_friendship_status(db: Session, db_friendship: models.Friendship, status: models.FriendshipStatus) -> models.Friendship:
    """Обновить статус заявки (принять/отклонить)."""
    db_friendship.status = status
    db.commit()
    db.refresh(db_friendship)
    return db_friendship

def delete_friendship(db: Session, db_friendship: models.Friendship):
    """Удалить дружбу или заявку."""
    db.delete(db_friendship)
    db.commit()

def are_users_friends(db: Session, user1_id: int, user2_id: int) -> bool:
    """Проверяет, являются ли два пользователя друзьями (статус ACCEPTED)."""
    friendship = db.query(models.Friendship).filter(
        (models.Friendship.status == models.FriendshipStatus.ACCEPTED) &
        or_(
            (models.Friendship.requester_id == user1_id) & (models.Friendship.addressee_id == user2_id),
            (models.Friendship.requester_id == user2_id) & (models.Friendship.addressee_id == user1_id)
        )
    ).first()
    return friendship is not None

def get_all_user_friendships(db: Session, user_id: int) -> TypingList[models.Friendship]:
    """Получить все связи (друзья, заявки) для пользователя."""
    return db.query(models.Friendship).options(
        joinedload(models.Friendship.requester),
        joinedload(models.Friendship.addressee)
    ).filter(
        or_(
            models.Friendship.requester_id == user_id,
            models.Friendship.addressee_id == user_id
        )
    ).all()

# --- CRUD для Списков ---

# ЗАМЕНЯЕМ get_public_lists_by_user НА ЭТУ ФУНКЦИЮ
def get_visible_lists_by_user(db: Session, profile_owner_id: int, viewer_id: int):
    """
    Получает списки пользователя, видимые для конкретного зрителя.
    - Если зритель и владелец - друзья, показывает public и friends_only списки.
    - Иначе, показывает только public списки.
    """
    # Сначала проверяем, являются ли пользователи друзьями
    are_friends = are_users_friends(db, user1_id=profile_owner_id, user2_id=viewer_id)

    query = db.query(models.List).filter(models.List.owner_id == profile_owner_id)

    if are_friends:
        # Если друзья, то разрешаем смотреть 'public' и 'friends_only'
        query = query.filter(
            or_(
                models.List.privacy_level == models.PrivacyLevel.PUBLIC,
                models.List.privacy_level == models.PrivacyLevel.FRIENDS_ONLY
            )
        )
    else:
        # Если не друзья, то только 'public'
        query = query.filter(models.List.privacy_level == models.PrivacyLevel.PUBLIC)

    return query.all()

def get_list(db: Session, list_id: int) -> Optional[models.List]:
    """Получить один список по его ID с полной информацией."""
    # Используем joinedload для оптимизации запросов к связанным таблицам
    return (
        db.query(models.List)
        .options(
            joinedload(models.List.items)
            .joinedload(models.Item.comments)
            .joinedload(models.Comment.owner)
        )
        .options(joinedload(models.List.items).joinedload(models.Item.likes))
        .filter(models.List.id == list_id)
        .first()
    )

# Новая функция для получения списка по публичному ключу
def get_list_by_public_key(db: Session, public_key: UUID) -> Optional[models.List]:
    """Получить один список по его публичному UUID ключу с полной информацией."""
    return (
        db.query(models.List)
        .options(joinedload(models.List.owner)) # <--- ДОБАВЛЕНА ЭТА СТРОКА
        .options(
            joinedload(models.List.items)
            .joinedload(models.Item.comments)
            .joinedload(models.Comment.owner)
        )
        .options(joinedload(models.List.items).joinedload(models.Item.likes))
        .filter(models.List.public_url_key == public_key)
        .first()
    )

def get_lists_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> TypingList[models.List]:
    """Получить все списки конкретного пользователя."""
    return db.query(models.List).filter(models.List.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_list(db: Session, list_data: schemas.ListCreate, user_id: int) -> models.List:
    """Создать новый список для пользователя."""
    db_list = models.List(**list_data.dict(), owner_id=user_id)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

def update_list(db: Session, db_list: models.List, list_data: schemas.ListUpdate) -> models.List:
    """Обновить существующий список."""
    update_data = list_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_list, key, value)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

def delete_list(db: Session, db_list: models.List):
    """Удалить список."""
    db.delete(db_list)
    db.commit()
    return db_list

# --- CRUD для Элементов ---

def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    """Получить один элемент по его ID."""
    # Используем joinedload, чтобы подтянуть список для проверки прав
    return db.query(models.Item).options(joinedload(models.Item.list)).filter(models.Item.id == item_id).first()

def create_list_item(db: Session, item_data: schemas.ItemCreate, list_id: int) -> models.Item:
    """Создать новый элемент в списке."""
    db_item = models.Item(**item_data.dict(), list_id=list_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, db_item: models.Item, item_data: schemas.ItemUpdate) -> models.Item:
    """Обновить существующий элемент."""
    update_data = item_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, db_item: models.Item):
    """Удалить элемент."""
    db.delete(db_item)
    db.commit()
    return db_item

# --- (Новое) CRUD для Копирования Элементов ---

def get_or_create_default_copy_list(db: Session, user_id: int) -> models.List:
    """Получает или создает список по умолчанию для скопированных элементов."""
    
    # 1. Поиск существующего списка
    default_list = db.query(models.List).filter(
        models.List.owner_id == user_id,
        models.List.title == DEFAULT_COPY_LIST_TITLE,
        models.List.list_type == models.ListType.WISHLIST 
    ).first()

    if default_list:
        return default_list

    # 2. Создание нового списка, если он не найден
    list_data = schemas.ListCreate(
        title=DEFAULT_COPY_LIST_TITLE,
        description="Сюда автоматически сохраняются элементы, скопированные из чужих списков.",
        list_type=models.ListType.WISHLIST,
        privacy_level=models.PrivacyLevel.PRIVATE 
    )
    
    db_list = models.List(**list_data.dict(), owner_id=user_id)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


def copy_item_to_list(db: Session, source_item: models.Item, target_user: models.User) -> models.Item:
    """Копирует данные элемента в список пользователя."""
    
    # 1. Получаем или создаем целевой список
    target_list = get_or_create_default_copy_list(db, target_user.id)
    
    # 2. Создаем новый элемент на основе исходного
    new_item_data = {
        'title': source_item.title,
        'description': source_item.description,
        'image_url': source_item.image_url,
        'thumbnail_url': source_item.thumbnail_url,
        'list_id': target_list.id
    }
    
    db_item = models.Item(**new_item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # 3. Возвращаем созданный элемент
    return db_item


# --- CRUD для Бронирования ---

def get_reservation_by_item_id(db: Session, item_id: int) -> Optional[models.Reservation]:
    """Получить бронирование по ID элемента."""
    return db.query(models.Reservation).filter(models.Reservation.item_id == item_id).first()

def get_reservations_by_user(db: Session, user_id: int) -> TypingList[models.Reservation]:
    """Получить все бронирования пользователя."""
    return db.query(models.Reservation).filter(models.Reservation.reserver_id == user_id).all()

def create_reservation(db: Session, item: models.Item, user: models.User) -> models.Reservation:
    """Создать новое бронирование."""
    db_reservation = models.Reservation(item_id=item.id, reserver_id=user.id)
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def delete_reservation(db: Session, db_reservation: models.Reservation):
    """Удалить бронирование."""
    db.delete(db_reservation)
    db.commit()
    return db_reservation

# --- CRUD для Лайков ---

def get_like(db: Session, item_id: int, user_id: int) -> Optional[models.Like]:
    """Получить лайк по ID элемента и ID пользователя."""
    return db.query(models.Like).filter(models.Like.item_id == item_id, models.Like.user_id == user_id).first()

def add_like(db: Session, item: models.Item, user: models.User) -> models.Like:
    """Добавить лайк."""
    db_like = models.Like(item_id=item.id, user_id=user.id)
    db.add(db_like)
    db.commit()
    db.refresh(db_like) # <-- Добавляем refresh

    if item.list.owner_id != user.id:
        create_notification(
            db,
            recipient_id=item.list.owner_id,
            sender_id=user.id,
            type=models.NotificationType.LIKE,
            related_item_id=item.id
        )
        db.refresh(db_like, attribute_names=['item']) # <-- Обновляем связи
    
    return db_like # <-- Возвращаем объект

def remove_like(db: Session, db_like: models.Like):
    """Удалить лайк."""
    db.delete(db_like)
    db.commit()
    return db_like

# --- CRUD для Комментариев ---

def get_comment(db: Session, comment_id: int) -> Optional[models.Comment]:
    """Получить комментарий по его ID."""
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def create_comment(db: Session, comment_data: schemas.CommentCreate, item_id: int, user_id: int) -> models.Comment:
    """Создать новый комментарий."""
    db_comment = models.Comment(**comment_data.dict(), item_id=item_id, owner_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    # (Новое) Получаем элемент, чтобы узнать владельца
    item = get_item(db, item_id)
    # Создаем уведомление для владельца элемента, если это не он сам
    if item and item.list.owner_id != user_id:
        create_notification(
            db,
            recipient_id=item.list.owner_id,
            sender_id=user_id,
            type=models.NotificationType.COMMENT,
            related_item_id=item.id
        )
        db.refresh(db_comment, attribute_names=['item']) # <-- Обновляем связи

    return db_comment

def delete_comment(db: Session, db_comment: models.Comment):
    """Удалить комментарий."""
    db.delete(db_comment)
    db.commit()
    return db_comment

# --- (Новое) CRUD для Уведомлений ---

def create_notification(db: Session, recipient_id: int, sender_id: int, type: models.NotificationType, related_item_id: Optional[int] = None):
    """Создать новое уведомление (без отправки WS)."""
    db_notification = models.Notification(
        recipient_id=recipient_id,
        sender_id=sender_id,
        type=type,
        related_item_id=related_item_id
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications_for_user(db: Session, user_id: int, limit: int = 20) -> TypingList[models.Notification]:
    """Получить все уведомления для пользователя, отсортированные по дате."""
    return db.query(models.Notification).options(
        joinedload(models.Notification.sender)
    ).filter(
        models.Notification.recipient_id == user_id
    ).order_by(models.Notification.created_at.desc()).limit(limit).all()

def count_unread_notifications(db: Session, user_id: int) -> int:
    """Подсчитать количество непрочитанных уведомлений."""
    return db.query(models.Notification).filter(
        models.Notification.recipient_id == user_id,
        models.Notification.is_read == False
    ).count()

def mark_notification_as_read(db: Session, notification_id: int, user_id: int) -> Optional[models.Notification]:
    """Пометить уведомление как прочитанное."""
    db_notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.recipient_id == user_id
    ).first()

    if db_notification and not db_notification.is_read:
        db_notification.is_read = True
        db.commit()
        db.refresh(db_notification)
        return db_notification
    return None
