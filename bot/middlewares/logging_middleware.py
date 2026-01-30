from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        event_type = "unknown"
        event_data = ""
        
        # Получаем информацию о событии
        if event.message:
            user = event.message.from_user
            event_type = "message"
            event_data = event.message.text or ""
        elif event.callback_query:
            user = event.callback_query.from_user
            event_type = "callback"
            event_data = event.callback_query.data or ""
        elif event.edited_message:
            user = event.edited_message.from_user
            event_type = "edited_message"
            event_data = event.edited_message.text or ""
        
        if user:
            user_info = f"ID: {user.id}, Имя: {user.username or user.first_name}"
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if event_type == "message" and event_data:
                log_message = f"[{current_time}] Пользователь {user_info}: команда '{event_data}'"
                logging.info(log_message)
                print(f"📝 {log_message}")
                
            elif event_type == "callback" and event_data:
                log_message = f"[{current_time}] Пользователь {user_info}: callback '{event_data}'"
                logging.info(log_message)
                print(f"🔄 {log_message}")
        
        # Логируем ошибки
        try:
            result = await handler(event, data)
            return result
        except Exception as e:
            user_info = f"ID: {user.id}" if user else "Неизвестный пользователь"
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_message = f"[{current_time}] ОШИБКА для пользователя {user_info}: {str(e)}"
            logging.error(error_message)
            print(f"❌ {error_message}")
            raise