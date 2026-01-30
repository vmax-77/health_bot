# handlers/progress.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile  # Изменяем импорт
from datetime import date
from database.crud import (
    get_user, get_water_today, 
    get_calories_today, get_burned_calories_today,
    get_weekly_summary
)
from services.visualizations import (
    create_daily_progress_chart,
    create_weekly_chart
)

router = Router()

@router.message(Command("check_progress"))
async def cmd_check_progress(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала настройте профиль командой /set_profile")
        return
    
    water_today = get_water_today(user['user_id'])
    calories_today = get_calories_today(user['user_id'])
    burned_today = get_burned_calories_today(user['user_id'])
    
    water_remaining = max(0, user['water_goal'] - water_today)
    calories_balance = calories_today - burned_today
    calories_remaining = max(0, user['calorie_goal'] - calories_balance)
    
    # Получаем график
    chart_buffer = await create_daily_progress_chart(
        water_consumed=water_today,
        water_goal=user['water_goal'],
        calories_consumed=calories_today,
        calories_burned=burned_today,
        calorie_goal=user['calorie_goal']
    )
    
    report = (
        f"📊 Ваш прогресс на {date.today().strftime('%d.%m.%Y')}\n\n"
        f"💧 Вода:\n"
        f"  ├ Выпито: {water_today:.0f} мл\n"
        f"  ├ Цель: {user['water_goal']:.0f} мл\n"
        f"  └ Осталось: {water_remaining:.0f} мл\n"
        f"    Прогресс: {(water_today / user['water_goal'] * 100):.1f}%\n\n"
        f"🔥 Калории:\n"
        f"  ├ Потреблено: {calories_today:.0f} ккал\n"
        f"  ├ Сожжено: {burned_today:.0f} ккал\n"
        f"  ├ Баланс: {calories_balance:.0f} ккал\n"
        f"  ├ Цель: {user['calorie_goal']:.0f} ккал\n"
        f"  └ Осталось: {calories_remaining:.0f} ккал\n"
        f"    Прогресс: {(calories_balance / user['calorie_goal'] * 100):.1f}%"
    )
    
    if chart_buffer:
        # Получаем байты из буфера
        chart_bytes = chart_buffer.getvalue()
        
        # Создаем BufferedInputFile
        photo = BufferedInputFile(chart_bytes, filename="progress.png")
        
        await message.answer_photo(
            photo=photo,
            caption=report
        )
    else:
        # Если график не создался, отправляем только текст
        await message.answer(report)
    
    await message.answer(
        "Посмотреть статистику за неделю: /weekly_stats"
    )

@router.message(Command("weekly_stats"))
async def cmd_weekly_stats(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала настройте профиль командой /set_profile")
        return
    
    weekly_data = get_weekly_summary(user['user_id'])
    
    report = "📈 Ваша недельная статистика\n\n"
    has_data = False
    
    for day_data in weekly_data:
        if day_data["date"]:
            date_str = day_data["date"].strftime("%d.%m")
            report += (
                f"{date_str}: "
                f"💧 {day_data['water']:.0f} мл | "
                f"🔥 {day_data['calories']:.0f} ккал | "
                f"🏃 {day_data['workouts']} тренировок\n"
            )
            has_data = True
    
    if not has_data:
        report += "Нет данных за последнюю неделю"
    
    # Пытаемся создать график
    chart_buffer = await create_weekly_chart(weekly_data)
    
    if chart_buffer:
        # Получаем байты из буфера
        chart_bytes = chart_buffer.getvalue()
        
        # Создаем BufferedInputFile
        photo = BufferedInputFile(chart_bytes, filename="weekly_stats.png")
        
        await message.answer_photo(
            photo=photo,
            caption=report
        )
    else:
        await message.answer(report)