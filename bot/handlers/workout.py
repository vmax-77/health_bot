# handlers/workout.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from database.crud import add_workout_log, get_user
from services.calculations import calculate_workout_calories

router = Router()

class WorkoutStates(StatesGroup):
    type = State()
    duration = State()

workout_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Бег"), KeyboardButton(text="Ходьба")],
        [KeyboardButton(text="Велосипед"), KeyboardButton(text="Плавание")],
        [KeyboardButton(text="Силовая"), KeyboardButton(text="Йога")],
        [KeyboardButton(text="Другое")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message, state: FSMContext):
    await message.answer("Выберите тип тренировки:", reply_markup=workout_kb)
    await state.set_state(WorkoutStates.type)

@router.message(WorkoutStates.type)
async def process_workout_type(message: Message, state: FSMContext):
    workout_type = message.text
    await state.update_data(workout_type=workout_type)
    await message.answer(
        "Введите длительность тренировки в минутах (например: 45):",
        reply_markup=None
    )
    await state.set_state(WorkoutStates.duration)

# Этот обработчик защищен состоянием!
@router.message(WorkoutStates.duration)
async def process_workout_duration(message: Message, state: FSMContext):
    try:
        duration = int(message.text)
        if duration <= 0 or duration > 300:
            await message.answer("Пожалуйста, введите корректную длительность (1-300 минут)")
            return
        
        data = await state.get_data()
        workout_type = data.get("workout_type")
        
        user = get_user(message.from_user.id)
        if not user:
            await message.answer("Сначала настройте профиль командой /set_profile")
            return
        
        calories_burned = calculate_workout_calories(
            workout_type=workout_type,
            duration=duration,
            weight=user['weight']
        )
        
        add_workout_log(
            user_id=message.from_user.id,
            workout_type=workout_type,
            duration=duration,
            calories_burned=calories_burned
        )
        
        extra_water = (duration // 30) * 200
        
        await message.answer(
            f"✅ Тренировка записана!\n\n"
            f"🏃‍♂️ Тип: {workout_type}\n"
            f"⏱ Длительность: {duration} мин\n"
            f"🔥 Сожжено калорий: {calories_burned:.0f}\n"
            f"💧 Рекомендуется дополнительно: {extra_water} мл воды"
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 45)")