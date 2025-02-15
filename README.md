# ii_bot

Telegram bot

Запуск приложения:

Устанавливаем зависимости
```bash
pip install -r requirements.txt
```
Далее нам необходимо создать в корневом каталоге `.env` файл. по аналогии с примеров в [env.example](env.example)
пояснения по переменным окружения:
все что касается 
TG_API_ID="https://my.telegram.org/apps"

В него прописываем:
```
# Settings logging
LEVEL="DEBUG"
GURU="True"
TRACEBACK="False"

# Settings Telegram  
TG_API_ID="https://my.telegram.org/apps"
TG_API_HASH="https://my.telegram.org/apps"
TG_BOT_TOKEN="https://my.telegram.org/apps"
TG_ADMIN_ID="123456789"

# Settings for RabbitMQ
RABBIT_USER="guest"
RABBIT_PASSWORD="guest"
RABBIT_HOST="0.0.0.0"
RABBIT_PORT="5672"
```


```bash
cd telegram_bot && python main.py
```

Создание контейнера:

```bash
  docker build  -t telegram_bot .
```
```bash
docker build -t vivera83/ii_bot:1 .
```  


```bash
docker push vivera83/ii_bot:1
```  

