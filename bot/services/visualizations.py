import matplotlib.pyplot as plt
import io
from typing import Dict, List

async def create_daily_progress_chart(water_consumed: float, water_goal: float,
                                     calories_consumed: float, calories_burned: float,
                                     calorie_goal: float):
    """Создание графика дневного прогресса - возвращает BytesIO или None"""
    try:
        # Проверяем валидность данных
        if water_goal <= 0 or calorie_goal <= 0:
            return None
            
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # График воды
        water_values = [water_consumed, max(0, water_goal - water_consumed)]
        water_labels = [f'Выпито\n{water_consumed:.0f} мл', f'Осталось\n{water_values[1]:.0f} мл']
        colors_water = ['#4CAF50', '#E0E0E0']
        
        axes[0].pie(water_values, labels=water_labels, colors=colors_water,
                    autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
                    startangle=90, textprops={'fontsize': 9})
        axes[0].set_title('Прогресс по воде', fontsize=14, fontweight='bold')
        
        # График калорий
        categories = ['Потреблено', 'Сожжено', 'Цель']
        values = [calories_consumed, calories_burned, calorie_goal]
        colors_calories = ['#FF9800', '#2196F3', '#4CAF50']
        
        bars = axes[1].bar(categories, values, color=colors_calories)
        axes[1].set_ylabel('Ккал', fontsize=12)
        axes[1].set_title('Баланс калорий', fontsize=14, fontweight='bold')
        
        # Добавляем значения на столбцы
        for bar, value in zip(bars, values):
            height = bar.get_height()
            axes[1].text(bar.get_x() + bar.get_width()/2., height + 10,
                        f'{value:.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Сохраняем в байты
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
        
    except Exception as e:
        print(f"Ошибка создания графика: {e}")
        return None

async def create_weekly_chart(weekly_data: List[Dict]):
    """Создание недельного графика"""
    if not weekly_data:
        return None
    
    try:
        dates = []
        water_values = []
        calorie_values = []
        
        for d in weekly_data:
            if d.get("date") and (d.get("water", 0) > 0 or d.get("calories", 0) > 0):
                dates.append(d["date"].strftime("%d.%m"))
                water_values.append(d.get("water", 0))
                calorie_values.append(d.get("calories", 0))
        
        if len(dates) < 2:  # Нужно минимум 2 точки для графика
            return None
        
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        
        # График воды
        axes[0].plot(dates, water_values, marker='o', color='#4CAF50', linewidth=2)
        axes[0].fill_between(dates, water_values, alpha=0.3, color='#4CAF50')
        axes[0].set_title('Потребление воды за неделю', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('мл', fontsize=12)
        axes[0].grid(True, alpha=0.3)
        
        # Добавляем значения на точки
        for i, (date, value) in enumerate(zip(dates, water_values)):
            axes[0].text(i, value + 50, f'{value:.0f}', ha='center', va='bottom', fontsize=8)
        
        # График калорий
        axes[1].plot(dates, calorie_values, marker='o', color='#FF9800', linewidth=2)
        axes[1].fill_between(dates, calorie_values, alpha=0.3, color='#FF9800')
        axes[1].set_title('Потребление калорий за неделю', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('ккал', fontsize=12)
        axes[1].set_xlabel('Дата', fontsize=12)
        axes[1].grid(True, alpha=0.3)
        
        # Добавляем значения на точки
        for i, (date, value) in enumerate(zip(dates, calorie_values)):
            axes[1].text(i, value + 50, f'{value:.0f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        # Сохраняем в байты
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
        
    except Exception as e:
        print(f"Ошибка создания недельного графика: {e}")
        return None