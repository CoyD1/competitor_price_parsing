# Competitor Price Tracker API

backend-проект для мониторинга цен конкурентов.

## Возможности

- CRUD товаров конкурентов
- Валидация входных данных через Pydantic
- Async SQLAlchemy + PostgreSQL
- Alembic-миграции
- История изменения цен
- Ручная запись проверки цены
- Парсинг цены по URL и CSS-селектору
- Unit-тесты парсера
- Ruff для проверки качества кода

## Стек

- Python
- FastAPI
- SQLAlchemy async
- PostgreSQL
- Alembic
- Pydantic
- HTTPX
- BeautifulSoup
- Pytest
- Ruff

## Установка

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\pip.exe install -r requirements.txt
```

## Настройка окружения

Создать файл `.env` на основе `.env.example`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/price_tracker
```

## Миграции

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

## Запуск API

```powershell
.\.venv\Scripts\uvicorn.exe main:app --reload --host 127.0.0.1 --port 8010
```

Swagger:

```text
http://127.0.0.1:8010/docs
```

## Тесты

```powershell
.\.venv\Scripts\pytest.exe
```

## Линтинг

```powershell
.\.venv\Scripts\ruff.exe check .
```

## Локальная проверка парсинга

Запуск тестовой HTML-страницы:

```powershell
.\.venv\Scripts\python.exe -m http.server 9000 --directory test_pages
```

Создание продукта через `POST /products/`:

```json
{
  "name": "Test Keyboard",
  "competitor_name": "Local Test Shop",
  "price": 1,
  "url": "http://127.0.0.1:9000/product.html",
  "price_selector": ".product-price"
}
```

Если вызвать:

```text
POST /products/{product_id}/parse-price
```

Цена должна обновиться на значение из HTML.

## Проверка Перед Коммитом

```powershell
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\pytest.exe
```
