FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requisitos
COPY requirements_export.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements_export.txt

# Copiar el código de la aplicación
COPY . .

# Variable de entorno para el puerto (Railway la configura automáticamente)
ENV PORT=5000
ENV FLASK_APP=main.py

# Comando para iniciar la aplicación
CMD gunicorn --bind 0.0.0.0:$PORT run_task_manager:app