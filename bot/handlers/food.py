from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from services.nutrition import search_food
from database.crud import (
    add_food_log, get_user, get_today_calories
)

router = Router()

class FoodStates(StatesGroup):
    searching = State()
    selecting = State()
    entering_amount = State()

@router.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext):
    await message.answer("Введите название продукта (например: 'банан' или 'куриная грудка'):")
    await state.set_state(FoodStates.searching)

@router.message(FoodStates.searching)
async def process_food_search(message: Message, state: FSMContext):
    query = message.text
    results = await search_food(query)
    
    if not results:
        await message.answer("Продукт не найден. Попробуйте другое название.")
        return
    
    await state.update_data(search_results=results)
    
    keyboard = []
    for i, product in enumerate(results[:5]):
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product['name']} ({product.get('calories', 0)} ккал/100г)",
                callback_data=f"select_food_{i}"
            )
        ])
    
    await message.answer(
        "Выберите продукт:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await state.set_state(FoodStates.selecting)

@router.callback_query(F.data.startswith("select_food_"))
async def process_food_selection(callback_query, state: FSMContext):
    data = await state.get_data()
    results = data.get("search_results", [])
    idx = int(callback_query.data.split("_")[-1])
    
    if idx < len(results):
        selected_food = results[idx]
        await state.update_data(selected_food=selected_food)
        
        await callback_query.message.answer(
            f"Вы выбрали: {selected_food['name']}\n"
            f"Калорийность: {selected_food.get('calories', 0)} ккал/100г\n\n"
            f"Введите количество в граммах (например: 150):"
        )
        await state.set_state(FoodStates.entering_amount)
    
    await callback_query.answer()

@router.message(FoodStates.entering_amount)
async def process_food_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0 or amount > 5000:
            await message.answer("Пожалуйста, введите корректное количество (1-5000 г)")
            return
        
        data = await state.get_data()
        selected_food = data.get("selected_food", {})
        
        calories_per_100g = selected_food.get("calories", 0)
        total_calories = (calories_per_100g * amount) / 100
        
        add_food_log(
            user_id=message.from_user.id,
            food_name=selected_food["name"],
            calories=total_calories,
            serving_size=amount
        )
        
        user = get_user(message.from_user.id)
        today_calories = get_today_calories(message.from_user.id)
        
        await message.answer(
            f"✅ Записано: {selected_food['name']}\n"
            f"📊 Количество: {amount:.0f} г\n"
            f"🔥 Калории: {total_calories:.1f} ккал\n"
            f"📈 Всего за день: {today_calories:.0f} / {user['calorie_goal']:.0f} ккал"
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 150)")