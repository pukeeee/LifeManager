import os
from dotenv import load_dotenv

# Завантажуємо змінні середовища з файлу .env
load_dotenv()

# Отримуємо конфігурацію з оточення
DB_URL = os.getenv("DB_URL")
CHANNEL = os.getenv("CHANNEL")
ADMIN_TG_ID = os.getenv("ADMIN_TG_ID")
IMG_FOLDER = "img"

# Константи, що є частиною логіки додатку, а не конфігурацією середовища
LEVEL = {1: 1, 2: 10, 3: 25, 4: 50}
TASK_BASE_EXP = 50
HABIT_BASE_EXP = 10
