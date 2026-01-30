def calculate_water_goal(weight: float, activity_level: str, temperature: float) -> float:
    """Расчет нормы воды"""
    # Базовая норма: 30 мл на кг веса
    base_water = weight * 30
    
    # Учет активности
    activity_multipliers = {
        "sedentary": 0,
        "light": 200,
        "moderate": 400,
        "active": 600,
        "very_active": 800
    }
    activity_water = activity_multipliers.get(activity_level, 0)
    
    # Учет температуры
    temperature_bonus = 0
    if temperature > 25:
        temperature_bonus = 500
    elif temperature > 30:
        temperature_bonus = 1000
    
    return base_water + activity_water + temperature_bonus

def calculate_calorie_goal(weight: float, height: float, age: int, 
                          gender: str, activity_level: str) -> float:
    """Расчет нормы калорий по формуле Миффлина-Сан Жеора"""
    # BMR (Basal Metabolic Rate)
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:  # female
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Умножаем на коэффициент активности
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.2)
    return bmr * multiplier

def calculate_workout_calories(workout_type: str, duration: int, weight: float) -> float:
    """Расчет сожженных калорий во время тренировки"""
    # MET (Metabolic Equivalent of Task) values
    met_values = {
        "Бег": 8.0,
        "Ходьба": 3.5,
        "Велосипед": 7.5,
        "Плавание": 6.0,
        "Силовая": 6.0,
        "Йога": 2.5,
        "Другое": 4.0
    }
    
    met = met_values.get(workout_type, 4.0)
    
    # Формула: калории = MET * вес (кг) * время (часы)
    calories = met * weight * (duration / 60)
    return calories

def calculate_goals(weight: float, height: float, age: int, 
                   gender: str, activity_level: str, temperature: float) -> dict:
    """Расчет всех целей"""
    water_goal = calculate_water_goal(weight, activity_level, temperature)
    calorie_goal = calculate_calorie_goal(weight, height, age, gender, activity_level)
    
    return {
        "water_goal": water_goal,
        "calorie_goal": calorie_goal
    }