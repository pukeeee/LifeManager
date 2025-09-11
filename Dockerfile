# Використовуємо офіційний образ Python
FROM python:3.12-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файл з залежностями
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо решту коду додатку
COPY . .

# Створюємо порожню теку для бази даних, якщо вона потрібна локально
RUN mkdir -p /app/database

# Вказуємо команду для запуску бота
CMD ["python", "run.py"]
