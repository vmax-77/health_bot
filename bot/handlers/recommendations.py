# handlers/recommendations.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime
from database.crud import (
    get_user, get_water_today, 
    get_calories_today, get_last_workout
)
from services.nutrition import get_low_calorie_foods

router = Router()

@router.message(Command("recommend"))
async def cmd_recommend(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала настройте профиль командой /set_profile")
        return
    
    water_today = get_water_today(user['user_id'])
    calories_today = get_calories_today(user['user_id'])
    last_workout = get_last_workout(user['user_id'])
    
    recommendations = []
    
    water_percentage = (water_today / user['water_goal']) * 100
    if water_percentage < 50:
        recommendations.append("💧 Вы пьете мало воды. Попробуйте выпить стакан прямо сейчас!")
    elif water_percentage < 80:
        recommendations.append("💧 Вода: хороший прогресс. Не забывайте пить регулярно.")
    
    calories_percentage = (calories_today / user['calorie_goal']) * 100
    current_hour = datetime.now().hour
    
    if calories_percentage > 90 and current_hour < 20:
        low_cal_foods = await get_low_calorie_foods()
        recommendations.append(
            f"🍽 Вы близки к дневной норме. "
            f"Рассмотрите легкие продукты:\n{', '.join(low_cal_foods[:3])}"
        )
    elif calories_percentage < 40 and current_hour > 15:
        recommendations.append("🍽 У вас еще много калорий до цели. Подумайте о полноценном ужине.")
    
    if last_workout:
        from datetime import datetime as dt
        days_since_last = (dt.now() - dt.fromisoformat(last_workout['timestamp'])).days
        if days_since_last > 2:
            recommendations.append(
                f"🏃‍♂️ Прошло {days_since_last} дней с последней тренировки. "
                f"Время для активности!"
            )
    else:
        recommendations.append("🏃‍♂️ Вы еще не тренировались сегодня. Как насчет 15-минутной зарядки?")
    
    if recommendations:
        response = "💡 **Персональные рекомендации:**\n\n" + "\n\n".join(recommendations)
    else:
        response = "✅ Вы отлично справляетесь! Продолжайте в том же духе."
    
    await message.answer(response, parse_mode="Markdown")