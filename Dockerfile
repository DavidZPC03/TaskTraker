FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements_export.txt .
RUN pip install --no-cache-dir -r requirements_export.txt

COPY . .

ENV PORT=5000

EXPOSE 5000

CMD gunicorn --bind 0.0.0.0:$PORT run_task_manager:app
