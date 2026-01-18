text
# WB Analytics Electra

Аналитическая панель для продавцов Wildberries на базе FastAPI, PostgreSQL, Redis и Celery.  
Проект предоставляет backend‑API для дашбордов по продажам, товарам и отчётам.

## Стек

- Python / FastAPI
- PostgreSQL
- Redis
- Celery (worker + beat)
- Docker / docker-compose
- JWT‑авторизация [web:88][web:90]

## Быстрый старт

Требования:

- Docker
- Docker Compose

Запуск:

```bash
docker-compose up -d
После успешного запуска будут доступны:

Backend: http://localhost:8000

Swagger UI: http://localhost:8000/docs

Авторизация
По умолчанию создаётся администратор:

text
email:    admin@electra.com
password: admin123
Вход через эндпоинт:

POST /api/v1/auth/login — получение access_token и refresh_token

POST /api/v1/auth/refresh

POST /api/v1/auth/logout

GET /api/v1/auth/me [conversation_history:19][web:88]

Авторизация в Swagger:

Войти в Swagger UI: http://localhost:8000/docs

Нажать кнопку Authorize

Ввести Bearer <access_token> из ответа на /api/v1/auth/login

Структура проекта (backend)
text
backend/
  Dockerfile
  requirements.txt
  app/
    main.py
    core/
      config.py
      dependencies.py
    db/
      base.py
      session.py
    models/
      __init__.py
      user.py
      cabinet.py
      product.py
      sales_history.py
      sync_history.py
    api/
      v1/
        routes/
          auth.py
          ...
Основные компоненты:

app/main.py — точка входа FastAPI‑приложения

app/db/session.py — настройка async‑подключения к PostgreSQL

app/models/*.py — SQLAlchemy‑модели (пользователи, кабинеты, товары, продажи, синки)

app/api/v1/routes/auth.py — эндпоинты авторизации [web:86][web:87]

docker-compose
Файл docker-compose.yml поднимает:

postgres — база данных (electra_db)

redis — брокер для Celery

backend — FastAPI‑приложение

celery_worker — обработка фоновых задач

celery_beat — планировщик задач [web:90][web:92]

Переменные окружения
Все настройки backend находятся в backend/.env (не хранится в репозитории):

Пример (упрощённый):

text
# Database
DATABASE_URL=postgresql+asyncpg://electra_user:electra_password@postgres:5432/electra_db

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption for WB API tokens
ENCRYPTION_KEY=...

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
Секреты (SECRET_KEY, ENCRYPTION_KEY, пароли, токены WB) не должны попадать в git. [web:59][web:64]

Планы по развитию
Экран «Главный дашборд» (выручка, заказы, топ‑товары)

Экран «Товары и продажи» (таблицы и графики по SKU)

Экран «Отчёты» (возвраты, платное хранение и др.)

Экран «Настройки и интеграции» (WB токен, расписание синков, пользователи)

Frontend (React/Vue/Svelte) с использованием текущего API [web:35][web:96]




