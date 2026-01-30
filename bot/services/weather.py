import aiohttp
from config import settings

async def get_current_temperature(city: str) -> float:
    """Получение текущей температуры для города"""
    url = "http://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": city,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["main"]["temp"]
                else:
                    raise Exception(f"Ошибка API: {response.status}")
        except Exception as e:
            # Возвращаем среднюю температуру по умолчанию
            return 20.0