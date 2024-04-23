FROM python:3.12.1
WORKDIR telegram_bot
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Settings logging
ENV LEVEL="INFO"
ENV GURU="True"
ENV TRACEBACK="false"

# Telegram application settings
ENV TG_API_ID=NULL
ENV TG_API_HASH=NULL
ENV TG_BOT_TOKEN=NULL
ENV TG_ADMIN_ID="-1"

# Settings for RabbitMQ
ENV RABBIT_USER="guest"
ENV RABBIT_PASSWORD="guest"
ENV RABBIT_HOST="host.docker.internal"
ENV RABBIT_PORT="5672"

# Building
RUN pip install --upgrade pip  --no-cache-dir
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY telegram_bot .

CMD python main.py