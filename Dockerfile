# Використовуємо легкий образ Python
FROM python:3.10-slim

# Робоча директорія в контейнері - корінь проекту
WORKDIR /project

# Встановлюємо PYTHONPATH на поточну робочу директорію
# Це дозволяє імпортувати 'simulation' з файлу 'app/streamlit_app.py'
ENV PYTHONPATH=/project

# Копіюємо requirements.txt та встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проекту
COPY . .

# Відкриваємо внутрішній порт Streamlit (буде прокинутий через docker-compose)
EXPOSE 8501
# Запуск додатку
# Streamlit CLI автоматично зчитає змінні STREAMLIT_SERVER_ADDRESS/PORT
CMD ["streamlit", "run", "app/streamlit_app.py"]