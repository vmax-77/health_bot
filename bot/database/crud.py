# database/crud.py
import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

def get_db_connection():
    """Получение соединения с БД"""
    return sqlite3.connect("fitness.db", check_same_thread=False)

def create_or_update_user(user_data: dict):
    """Создание или обновление пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверяем существование пользователя
    cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_data["user_id"],))
    user_exists = cursor.fetchone()
    
    if user_exists:
        # Обновляем существующего пользователя
        update_fields = []
        values = []
        for key, value in user_data.items():
            if key != "user_id":
                update_fields.append(f"{key} = ?")
                values.append(value)
        
        values.append(user_data["user_id"])
        query = f"UPDATE users SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
        cursor.execute(query, values)
    else:
        # Создаем нового пользователя
        columns = list(user_data.keys())
        placeholders = ["?"] * len(columns)
        values = list(user_data.values())
        
        query = f"INSERT INTO users ({', '.join(columns)}, created_at, updated_at) VALUES ({', '.join(placeholders)}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        cursor.execute(query, values)
    
    conn.commit()
    conn.close()

def get_user(user_id: int):
    """Получение пользователя по ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "user_id": row[1],
            "username": row[2],
            "weight": row[3],
            "height": row[4],
            "age": row[5],
            "gender": row[6],
            "activity_level": row[7],
            "city": row[8],
            "calorie_goal": row[9],
            "water_goal": row[10],
            "created_at": row[11],
            "updated_at": row[12]
        }
    return None

def add_water_log(user_id: int, amount: float):
    """Добавление записи о выпитой воде"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO water_logs (user_id, amount) VALUES (?, ?)",
        (user_id, amount)
    )
    
    conn.commit()
    conn.close()

def add_food_log(user_id: int, food_name: str, calories: float, serving_size: float):
    """Добавление записи о еде"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO food_logs (user_id, food_name, calories, serving_size) 
           VALUES (?, ?, ?, ?)""",
        (user_id, food_name, calories, serving_size)
    )
    
    conn.commit()
    conn.close()

def add_workout_log(user_id: int, workout_type: str, duration: int, calories_burned: float):
    """Добавление записи о тренировке"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO workout_logs (user_id, workout_type, duration, calories_burned) 
           VALUES (?, ?, ?, ?)""",
        (user_id, workout_type, duration, calories_burned)
    )
    
    conn.commit()
    conn.close()

def get_water_today(user_id: int) -> float:
    """Получение выпитой воды за сегодня"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT COALESCE(SUM(amount), 0) 
           FROM water_logs 
           WHERE user_id = ? AND DATE(timestamp) = DATE('now')""",
        (user_id,)
    )
    
    total = cursor.fetchone()[0]
    conn.close()
    return float(total)

def get_calories_today(user_id: int) -> float:
    """Получение потребленных калорий за сегодня"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT COALESCE(SUM(calories), 0) 
           FROM food_logs 
           WHERE user_id = ? AND DATE(timestamp) = DATE('now')""",
        (user_id,)
    )
    
    total = cursor.fetchone()[0]
    conn.close()
    return float(total)

def get_burned_calories_today(user_id: int) -> float:
    """Получение сожженных калорий за сегодня"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT COALESCE(SUM(calories_burned), 0) 
           FROM workout_logs 
           WHERE user_id = ? AND DATE(timestamp) = DATE('now')""",
        (user_id,)
    )
    
    total = cursor.fetchone()[0]
    conn.close()
    return float(total)

def get_last_workout(user_id: int):
    """Получение последней тренировки"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT * FROM workout_logs 
           WHERE user_id = ? 
           ORDER BY timestamp DESC LIMIT 1""",
        (user_id,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "user_id": row[1],
            "workout_type": row[2],
            "duration": row[3],
            "calories_burned": row[4],
            "timestamp": row[5]
        }
    return None

def get_weekly_summary(user_id: int) -> List[Dict]:
    """Получение недельной статистики - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Создаем временную таблицу с датами последних 7 дней
    cursor.execute("""
        WITH RECURSIVE dates(date) AS (
            SELECT DATE('now', '-6 days')
            UNION ALL
            SELECT DATE(date, '+1 day')
            FROM dates
            WHERE date < DATE('now')
        )
        SELECT 
            dates.date as date,
            COALESCE(SUM(w.amount), 0) as water,
            COALESCE(SUM(f.calories), 0) as calories,
            COUNT(DISTINCT wo.id) as workouts
        FROM dates
        LEFT JOIN water_logs w ON DATE(w.timestamp) = dates.date AND w.user_id = ?
        LEFT JOIN food_logs f ON DATE(f.timestamp) = dates.date AND f.user_id = ?
        LEFT JOIN workout_logs wo ON DATE(wo.timestamp) = dates.date AND wo.user_id = ?
        GROUP BY dates.date
        ORDER BY dates.date
    """, (user_id, user_id, user_id))
    
    rows = cursor.fetchall()
    conn.close()
    
    summary = []
    for row in rows:
        summary.append({
            "date": datetime.strptime(row[0], "%Y-%m-%d").date() if row[0] else None,
            "water": float(row[1]) if row[1] else 0.0,
            "calories": float(row[2]) if row[2] else 0.0,
            "workouts": row[3] or 0
        })
    
    return summary

def get_today_calories(user_id: int) -> float:
    """Получение потребленных калорий за сегодня"""
    return get_calories_today(user_id)