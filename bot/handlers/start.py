# handlers/start.py - ВОССТАНАВЛИВАЕМ ОБРАБОТЧИКИ КНОПОК
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database.crud import get_user
from keyboards.main_menu import get_main_menu_keyboard, get_profile_setup_keyboard

from handlers.profile import cmd_set_profile

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    user = get_user(message.from_user.id)
    
    if user:
        welcome_text = (
            f"👋 С возвращением, {message.from_user.first_name}!\n\n"
            f"🎯 Ваши текущие цели:\n"
            f"• 💧 Вода: {user['water_goal']:.0f} мл/день\n"
            f"• 🔥 Калории: {user['calorie_goal']:.0f} ккал/день\n\n"
            f"📊 Для просмотра прогресса используйте команду /check_progress\n"
            f"📝 Или выберите действие в меню ниже:"
        )
        
        keyboard = get_main_menu_keyboard()
    else:
        welcome_text = (
            f"🎉 Добро пожаловать, {message.from_user.first_name}!\n\n"
            f"Я — ваш персональный фитнес-помощник 🤖\n"
            f"Помогу отслеживать:\n"
            f"• 💧 Норму воды\n"
            f"• 🔥 Баланс калорий\n"
            f"• 🏃‍♂️ Тренировки и активность\n\n"
            f"📱 Для начала работы нужно настроить профиль."
        )
        
        keyboard = get_profile_setup_keyboard()
    
    # Без parse_mode
    await message.answer(
        welcome_text,
        reply_markup=keyboard
    )

@router.message(F.text == "🚀 Начать настройку профиля")
async def start_profile_setup(message: Message, state: FSMContext):
    await cmd_set_profile(message, state)

@router.message(F.text == "ℹ️ Как это работает?")
async def how_it_works(message: Message):
    await message.answer(
        "🤔 Как это работает?\n\n"
        "1. Настройте профиль (/set_profile)\n"
        "2. Записывайте воду, еду и тренировки\n"
        "3. Следите за прогрессом\n"
        "4. Получайте рекомендации\n\n"
        "📱 Все данные сохраняются автоматически!"
    )

@router.message(F.text == "📋 Список команд")
async def command_list(message: Message):
    await cmd_help(message)

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Справка"""
    help_text = (
        "📋 Основные команды:\n\n"
        "👤 Профиль:\n"
        "/set_profile - Настройка профиля\n"
        "/my_profile - Мой профиль\n\n"
        
        "💧 Вода:\n"
        "/log_water - Записать воду\n"
        "/water_250 - 250 мл воды\n"
        "/water_500 - 500 мл воды\n\n"
        
        "🍎 Питание:\n"
        "/log_food - Записать еду\n\n"
        
        "🏃‍♂️ Тренировки:\n"
        "/log_workout - Записать тренировку\n\n"
        
        "📊 Отчеты:\n"
        "/check_progress - Текущий прогресс\n"
        "/weekly_stats - Недельная статистика\n\n"
        
        "💡 Рекомендации:\n"
        "/recommend - Персональные рекомендации"
    )
    
    await message.answer(help_text)

# ВОССТАНАВЛИВАЕМ ОБРАБОТЧИКИ КНОПОК
@router.message(F.text == "💧 Вода")
async def water_button(message: Message):
    """Обработка кнопки Вода"""
    await message.answer(
        "💧 Запись воды:\n\n"
        "Используйте команды:\n"
        "/water_250 - Стакан воды (250мл)\n"
        "/water_500 - Бутылка воды (500мл)\n"
        "/log_water - Другое количество"
    )

@router.message(F.text == "🍎 Еда")
async def food_button(message: Message):
    """Обработка кнопки Еда"""
    await message.answer("🍎 Для записи еды используйте команду /log_food")

@router.message(F.text == "🏃‍♂️ Тренировка")
async def workout_button(message: Message):
    """Обработка кнопки Тренировка"""
    await message.answer("🏃‍♂️ Для записи тренировки используйте команду /log_workout")

@router.message(F.text == "📊 Прогресс")
async def progress_button(message: Message):
    """Обработка кнопки Прогресс"""
    await message.answer("📊 Для просмотра прогресса используйте команду /check_progress")

@router.message(F.text == "⚙️ Настройки")
async def settings_button(message: Message):
    """Обработка кнопки Настройки"""
    await message.answer(
        "⚙️ Настройки бота:\n\n"
        "Используйте команды:\n"
        "/my_profile - Просмотр профиля\n"
        "/set_profile - Изменить профиль\n"
        "/reset - Сбросить данные"
    )

@router.message(F.text == "💡 Рекомендации")
async def recommendations_button(message: Message):
    """Обработка кнопки Рекомендации"""
    from handlers.recommendations import cmd_recommend
    await cmd_recommend(message)

@router.message(F.text == "👤 Профиль")
async def profile_button(message: Message):
    """Обработка кнопки Профиль"""
    await message.answer(
        "👤 Управление профилем:\n\n"
        "Используйте команды:\n"
        "/my_profile - Просмотр профиля\n"
        "/set_profile - Изменить профиль"
    )

@router.message(F.text == "ℹ️ Помощь")
async def help_button(message: Message):
    """Обработка кнопки Помощь"""
    await cmd_help(message)

@router.message(Command("my_profile"))
async def cmd_my_profile(message: Message):
    """Просмотр профиля"""
    user = get_user(message.from_user.id)
    
    if not user:
        await message.answer("📋 Профиль не найден. Используйте /set_profile")
        return
    
    activity_map = {
        "sedentary": "Сидячий",
        "light": "Лёгкий",
        "moderate": "Умеренный",
        "active": "Активный",
        "very_active": "Очень активный"
    }
    
    activity_ru = activity_map.get(user['activity_level'], "Не указано")
    gender_ru = "Мужской" if user['gender'] == "male" else "Женский"
    
    profile_text = (
        f"👤 Ваш профиль\n\n"
        f"📊 Основные данные:\n"
        f"• Вес: {user['weight'] or 'Не указано'} кг\n"
        f"• Рост: {user['height'] or 'Не указано'} см\n"
        f"• Возраст: {user['age'] or 'Не указано'} лет\n"
        f"• Пол: {gender_ru}\n"
        f"• Активность: {activity_ru}\n"
        f"• Город: {user['city'] or 'Не указано'}\n\n"
        
        f"🎯 Цели:\n"
        f"• 💧 Вода: {user['water_goal'] or 2000} мл/день\n"
        f"• 🔥 Калории: {user['calorie_goal'] or 2000} ккал/день"
    )
    
    await message.answer(profile_text)