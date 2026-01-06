FROM python:3.12-slim

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libfreetype6-dev \
    libjpeg-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . .

# Estáticos
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "ImobCloud.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]