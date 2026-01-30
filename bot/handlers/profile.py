# handlers/profile.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from services.calculations import (
    calculate_water_goal, 
    calculate_calorie_goal
)
from services.weather import get_current_temperature
from database.crud import create_or_update_user

router = Router()

class ProfileStates(StatesGroup):
    weight = State()
    height = State()
    age = State()
    gender = State()
    activity = State()
    city = State()

gender_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

activity_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сидячий"), KeyboardButton(text="Лёгкий")],
        [KeyboardButton(text="Умеренный"), KeyboardButton(text="Активный")],
        [KeyboardButton(text="Очень активный")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    await message.answer("Давайте настроим ваш профиль!\nВведите ваш вес в кг:")
    await state.set_state(ProfileStates.weight)

@router.message(ProfileStates.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight < 20 or weight > 300:
            raise ValueError
        await state.update_data(weight=weight)
        await message.answer("Введите ваш рост в см:")
        await state.set_state(ProfileStates.height)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный вес (например: 75.5)")

@router.message(ProfileStates.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        if height < 100 or height > 250:
            raise ValueError
        await state.update_data(height=height)
        await message.answer("Введите ваш возраст:")
        await state.set_state(ProfileStates.age)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный рост (например: 180)")

@router.message(ProfileStates.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 10 or age > 120:
            raise ValueError
        await state.update_data(age=age)
        await message.answer("Выберите ваш пол:", reply_markup=gender_kb)
        await state.set_state(ProfileStates.gender)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст (например: 25)")

@router.message(ProfileStates.gender, F.text.in_(["Мужской", "Женский"]))
async def process_gender(message: Message, state: FSMContext):
    gender_map = {"Мужской": "male", "Женский": "female"}
    await state.update_data(gender=gender_map[message.text])
    await message.answer("Выберите уровень активности:", reply_markup=activity_kb)
    await state.set_state(ProfileStates.activity)

@router.message(ProfileStates.activity)
async def process_activity(message: Message, state: FSMContext):
    activity_map = {
        "Сидячий": "sedentary",
        "Лёгкий": "light",
        "Умеренный": "moderate",
        "Активный": "active",
        "Очень активный": "very_active"
    }
    
    if message.text not in activity_map:
        await message.answer("Пожалуйста, выберите вариант из клавиатуры")
        return
    
    await state.update_data(activity_level=activity_map[message.text])
    await message.answer("Введите ваш город:", reply_markup=None)
    await state.set_state(ProfileStates.city)

@router.message(ProfileStates.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    
    data = await state.get_data()

    try:
        temperature = await get_current_temperature(city)
        temperature_info = f"🌡 Температура в {city}: {temperature:.1f}°C\n\n"
    except Exception as e:
        temperature = 20.0
        temperature_info = f"🌡 Не удалось получить температуру для {city}, используем 20°C\n\n"
    
    water_goal = calculate_water_goal(
        weight=data['weight'], 
        activity_level=data['activity_level'],
        temperature=temperature
    )
    
    calorie_goal = calculate_calorie_goal(
        weight=data['weight'],
        height=data['height'],
        age=data['age'],
        gender=data['gender'],
        activity_level=data['activity_level']
    )
    
    user_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username or message.from_user.first_name,
        "weight": data['weight'],
        "height": data['height'],
        "age": data['age'],
        "gender": data['gender'],
        "activity_level": data['activity_level'],
        "city": city,
        "water_goal": water_goal,
        "calorie_goal": calorie_goal
    }
    
    create_or_update_user(user_data)
    
    response_text = (
        f"✅ Профиль сохранен!\n\n"
        f"{temperature_info}"
        f"📊 Ваши данные:\n"
        f"• Вес: {data['weight']} кг\n"
        f"• Рост: {data['height']} см\n"
        f"• Возраст: {data['age']} лет\n"
        f"• Пол: {data['gender']}\n"
        f"• Активность: {data['activity_level']}\n"
        f"• Город: {city}\n\n"
        f"🎯 Рассчитанные цели:\n"
        f"• 💧 Вода: {water_goal:.0f} мл/день\n"
        f"• 🔥 Калории: {calorie_goal:.0f} ккал/день"
    )
    
    await message.answer(response_text)
    await state.clear()