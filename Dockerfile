# Використовуємо легкий образ Python
FROM python:3.11

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

# Запуск додатку
# Streamlit CLI автоматично зчитає змінні STREAMLIT_SERVER_ADDRESS/PORT
CMD ["streamlit", "run", "app/streamlit_app.py"]