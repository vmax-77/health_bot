from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.crud import (
    get_user, add_water_log, 
    get_water_today
)

router = Router()

async def process_water(message: Message, amount: float):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала настройте профиль командой /set_profile")
        return
    
    add_water_log(message.from_user.id, amount)
    
    today_water = get_water_today(message.from_user.id)
    
    await message.answer(
        f"✅ Записано: {amount:.0f} мл воды\n"
        f"💧 Сегодня выпито: {today_water:.0f} мл\n"
        f"🎯 Цель: {user['water_goal']:.0f} мл\n"
        f"📊 Прогресс: {(today_water / user['water_goal'] * 100):.1f}%"
    )

@router.message(Command("log_water"))
async def cmd_log_water(message: Message):
    """Команда для логирования воды - просто показывает инструкцию"""
    await message.answer(
        "Введите количество воды в мл (например: 250):\n"
        "Или используйте быстрые команды:\n"
        "/water_250 - Стакан воды\n"
        "/water_500 - Бутылка воды"
    )

@router.message(Command("water_250"))
async def cmd_water_250(message: Message):
    await process_water(message, 250)

@router.message(Command("water_500"))
async def cmd_water_500(message: Message):
    await process_water(message, 500)

# УДАЛЯЕМ глобальный обработчик чисел - он конфликтует!
# Вместо этого добавим команду для ввода произвольного количества
@router.message(Command("water"))
async def cmd_water_input(message: Message):
    """Обработка команды /water <количество>"""
    try:
        # Получаем количество из аргументов команды
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Используйте: /water <количество> (например: /water 300)")
            return
        
        amount = float(parts[1])
        if amount <= 0 or amount > 5000:
            await message.answer("Пожалуйста, введите корректное количество (1-5000 мл)")
            return
        
        await process_water(message, amount)
        
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: /water 300)")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")