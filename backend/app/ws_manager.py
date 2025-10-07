# backend/app/ws_manager.py
from typing import Dict, List
from fastapi import WebSocket
import json
from . import schemas # <-- Добавить импорт
from . import models # <-- Добавить импорт

class ConnectionManager:
    def __init__(self):
        # Словарь для хранения активных соединений: {user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Принимает новое WebSocket соединение."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        """Отключает пользователя."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """Отправляет личное сообщение конкретному пользователю."""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(json.dumps(message))

# Создаем глобальный экземпляр менеджера
manager = ConnectionManager()


# --- НОВАЯ АСИНХРОННАЯ ФУНКЦИЯ ДЛЯ ФОНОВЫХ ЗАДАЧ ---
async def send_notification_ws(notification: models.Notification):
    """
    Подготавливает и отправляет данные уведомления через WebSocket.
    Предназначена для вызова через BackgroundTasks.
    """
    recipient_id = notification.recipient_id
    
    # Собираем данные для отправки через WS
    list_id = notification.related_item.list_id if notification.related_item else None
    
    notification_data = schemas.NotificationRead.from_orm(notification).dict()
    notification_data['related_list_id'] = list_id
    notification_data['sender'] = schemas.UserInComment.from_orm(notification.sender).dict()
    notification_data['created_at'] = notification.created_at.isoformat()

    await manager.send_personal_message(notification_data, recipient_id)