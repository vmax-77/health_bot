from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    weight = Column(Float)  # кг
    height = Column(Float)  # см
    age = Column(Integer)
    gender = Column(String(10), default="male")
    activity_level = Column(String(20), default="moderate")
    city = Column(String(100))
    calorie_goal = Column(Float, default=2000)
    water_goal = Column(Float, default=2000)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WaterLog(Base):
    __tablename__ = "water_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float)  # мл
    timestamp = Column(DateTime, default=datetime.utcnow)

class FoodLog(Base):
    __tablename__ = "food_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    food_name = Column(String(200))
    calories = Column(Float)
    protein = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    serving_size = Column(Float)  # граммы
    timestamp = Column(DateTime, default=datetime.utcnow)

class WorkoutLog(Base):
    __tablename__ = "workout_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    workout_type = Column(String(100))
    duration = Column(Integer)  # минуты
    calories_burned = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)