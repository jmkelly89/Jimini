FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# Render/Railway/Fly all inject $PORT at runtime; shell form lets it expand.
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 app:app
