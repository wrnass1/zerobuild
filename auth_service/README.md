# Auth Service

Сервис авторизации: регистрация, вход (JWT), профиль пользователя.

## Эндпоинты

| Метод | Путь      | Описание                    | Авторизация |
|-------|-----------|-----------------------------|-------------|
| POST  | /register | Регистрация                 | —           |
| POST  | /login    | Вход (получить JWT)         | —           |
| GET   | /profile  | Получить профиль            | Bearer JWT  |
| PUT   | /profile  | Обновить профиль            | Bearer JWT  |

## Swagger

После запуска сервиса:

- **Swagger UI:** http://localhost:8000/docs  
- **ReDoc:** http://localhost:8000/redoc  
- **OpenAPI JSON:** http://localhost:8000/openapi.json  

В Swagger для вызова GET/PUT `/profile` нажмите **Authorize**, вставьте токен из `/login` или `/register` (без слова "Bearer").

## Запуск

Из корня проекта:

```bash
docker-compose up --build
```

Сервис будет доступен на порту 8000. Для локального запуска без Docker нужен запущенный PostgreSQL и переменная `AUTH_DATABASE_URL` (или значение по умолчанию в `config.py`).
