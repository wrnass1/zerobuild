# Auth Service

Сервис авторизации: регистрация, вход (JWT), профиль пользователя.

## Статус по шагам авторизации

- **Инфраструктура**: PostgreSQL поднимается в Docker (`auth-db` в `docker-compose.yml`), `auth-service` подключается по `AUTH_DATABASE_URL`.
- **Код**: SQLAlchemy (async) подключён в `database.py`, Alembic добавлен в зависимости и настроен в `alembic/` + `alembic.ini`.
- **Модели**: SQLAlchemy-модель `User` описана в `models.py`, Pydantic-схемы (`UserRegister`, `UserLogin`, `ProfileUpdate`, `ProfileResponse`, `Token`) — в `schemas.py`.
- **Миграции**: создана первая миграция `0001_create_users_table` (таблица `users`), запускается через Alembic.
- **CRUD**: все эндпоинты (`/register`, `/login`, `/profile`) работают с PostgreSQL через SQLAlchemy, in‑memory хранилища нет.
- **Проверка**: API задокументирован, проверяется через Swagger (`/docs`) — данные сохраняются в БД.

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

## Миграции (Alembic)

- **Инициализация окружения** уже настроена в папке `alembic/`, использовать повторный `alembic init` не нужно.
- **Первая миграция**: `alembic/versions/0001_create_users_table.py` — создаёт таблицу `users` под текущую модель.

Команды (из папки `auth_service`):

```bash
alembic upgrade head      # применить все миграции
alembic downgrade -1      # откатить одну миграцию
```
