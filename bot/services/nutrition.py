import aiohttp
from typing import List, Dict, Optional

async def search_food(query: str) -> List[Dict]:
    """Поиск продуктов в OpenFoodFacts"""
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10,
        "fields": "product_name,nutriments"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    products = []
                    
                    for product in data.get("products", []):
                        if "product_name" in product and "nutriments" in product:
                            nutriments = product["nutriments"]
                            products.append({
                                "name": product["product_name"],
                                "calories": nutriments.get("energy-kcal_100g", 0),
                                "protein": nutriments.get("proteins_100g", 0),
                                "carbs": nutriments.get("carbohydrates_100g", 0),
                                "fat": nutriments.get("fat_100g", 0)
                            })
                    
                    return products
        except:
            pass
    
    # Если API недоступен, используем локальную базу
    return get_food_from_local_db(query)

def get_food_from_local_db(query: str) -> List[Dict]:
    """Локальная база популярных продуктов"""
    local_foods = {
        "банан": {"name": "Банан", "calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
        "яблоко": {"name": "Яблоко", "calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
        "куриная грудка": {"name": "Куриная грудка", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
        "рис": {"name": "Рис вареный", "calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
        "яйцо": {"name": "Яйцо куриное", "calories": 155, "protein": 13, "carbs": 1.1, "fat": 11},
        "овсянка": {"name": "Овсянка", "calories": 389, "protein": 16.9, "carbs": 66, "fat": 6.9},
    }
    
    results = []
    query_lower = query.lower()
    
    for name, data in local_foods.items():
        if query_lower in name or name in query_lower:
            results.append(data)
    
    return results

# Открой bot/services/nutrition.py и добавь:
async def get_food_details(food_id):
    """Заглушка для получения деталей еды"""
    return {
        "name": f"Продукт {food_id}",
        "calories": 100,
        "protein": 10,
        "carbs": 20,
        "fat": 5
    }

async def get_low_calorie_foods() -> List[str]:
    """Получить список низкокалорийных продуктов"""
    return [
        "Огурец (15 ккал/100г)",
        "Сельдерей (16 ккал/100г)",
        "Помидор (18 ккал/100г)",
        "Брокколи (34 ккал/100г)",
        "Цветная капуста (25 ккал/100г)",
        "Шпинат (23 ккал/100г)"
    ]