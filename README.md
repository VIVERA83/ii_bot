# ii_bot

Telegram bot

Запуск приложения:

1. Устанавливаем зависимости 
    ```bash
    pip install -r requirements.txt
    ```
2. Создать в корневом каталоге `.env` файл. По аналогии с примеров в [env.example](env.example)
за подробностями идем [сюда](docs/telegram.md)
3. Запуск, переходим в [telegram_bot](telegram_bot) и запускаем `main.py`. Перед запуском убедитесь что запущен RabbitMQ или указаны корректные данные для подключения к нему в переменных окружения
    ```bash
    cd telegram_bot && python main.py
    ```

Запуск приложения в Docker:
```bash
   docker compose up --build -d
```