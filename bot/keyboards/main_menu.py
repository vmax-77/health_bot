# keyboards/main_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Основное меню для пользователей с профилем"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="💧 Вода"), 
                KeyboardButton(text="🍎 Еда"),
                KeyboardButton(text="🏃‍♂️ Тренировка")
            ],
            [
                KeyboardButton(text="📊 Прогресс"),
                KeyboardButton(text="💡 Рекомендации"),
                KeyboardButton(text="👤 Профиль")
            ],
            [
                KeyboardButton(text="⚙️ Настройки"),
                KeyboardButton(text="ℹ️ Помощь")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

def get_profile_setup_keyboard() -> ReplyKeyboardMarkup:
    """Меню для новых пользователей"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Начать настройку профиля")],
            [KeyboardButton(text="ℹ️ Как это работает?")],
            [KeyboardButton(text="📋 Список команд")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Начните с настройки профиля..."
    )