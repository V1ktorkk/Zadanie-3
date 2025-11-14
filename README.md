# Глоссарий Децентрализованных Приложений (DApps) - Web API

Полнофункциональное REST API приложение для управления глоссарием терминов в области разработки децентрализованных приложений, построенное на FastAPI с валидацией данных через Pydantic и контейнеризацией в Docker.

## Основные возможности

- **Полный CRUD функционал** для управления глоссарием терминов
- **Валидация данных** через Pydantic модели
- **Полнотекстовый поиск** по терминам
- **Автоматическая документация** API через Swagger (OpenAPI)
- **Docker контейнеризация** для развертывания
- **Статистика** по глоссарию
- **Пагинация** при получении списков

## операции

✅ **Получение списка всех терминов** - `GET /api/glossary`
✅ **Получение информации о конкретном термине** - `GET /api/glossary/{term_id}`
✅ **Поиск по ключевому слову** - `GET /api/glossary/search/{keyword}`
✅ **Добавление нового термина** - `POST /api/glossary`
✅ **Обновление существующего термина** - `PUT /api/glossary/{term_id}`
✅ **Удаление термина** - `DELETE /api/glossary/{term_id}`

## Структура

```

│── __init__.py
│├── main.py                 # Основное приложение FastAPI
│└── glossary_data.json      # Начальные данные (22 термина)
├── Dockerfile                  # Docker образ
├── docker-compose.yml          # Docker Compose конфиг
├── requirements.txt            # Python зависимости
├── README.md                   # Документация
```

### Локальная установка

```bash
git clone https://github.com/yourusername/glossary-dapp.git
cd glossary-dapp

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```

### Docker

```bash
docker build -t glossary-dapp:latest .

docker run -p 8000:8000 --name glossary-api glossary-dapp:latest
```

### Docker Compose

```bash
docker-compose up -d

docker-compose logs -f glossary-api

docker-compose down
```

## API Документация

### 1. Получение всех терминов

```bash
GET /api/glossary?skip=0&limit=10
```

**Параметры:**

- `skip` (int, optional): Количество элементов для пропуска (по умолчанию 0)
- `limit` (int, optional): Максимальное количество элементов (по умолчанию 100)

**Пример ответа:**

```json
{
  "success": true,
  "message": "Получено 10 терминов из 22 всего",
  "data": {
    "total": 22,
    "skip": 0,
    "limit": 10,
    "items": [...]
  }
}
```

### 2. Получение конкретного термина

```bash
GET /api/glossary/1
```

**Пример ответа:**

```json
{
  "success": true,
  "message": "Термин найден",
  "data": {
    "id": 1,
    "title": "Децентрализованное приложение (DApp)",
    "definition": "Приложение, которое работает на децентрализованной сети...",
    "category": "Основные концепции",
    "examples": ["Uniswap", "OpenSea"],
    "related_terms": ["Блокчейн", "Смарт-контракт"],
    "source": "Ethereum documentation",
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T10:00:00"
  }
}
```

### 3. Поиск по ключевому слову

```bash
GET /api/glossary/search/блокчейн
```

**Пример ответа:**

```json
{
  "success": true,
  "message": "Найдено 5 терминов",
  "data": [
    {...},
    {...}
  ]
}
```

### 4. Добавление нового термина

```bash
POST /api/glossary
Content-Type: application/json

{
  "title": "Новый термин",
  "definition": "Определение этого нового термина с достаточно подробным описанием",
  "category": "Категория",
  "examples": ["пример1", "пример2"],
  "related_terms": ["связанный_термин"],
  "source": "Источник информации"
}
```

**Требуемые поля:**

- `title` (string, 1-100 символов): Название термина
- `definition` (string, минимум 10 символов): Определение

**Опциональные поля:**

- `category` (string): Категория термина
- `examples` (array): Примеры использования
- `related_terms` (array): Связанные термины
- `source` (string): Источник информации

### 5. Обновление термина

```bash
PUT /api/glossary/1
Content-Type: application/json

{
  "definition": "Обновленное определение термина"
}
```

### 6. Удаление термина

```bash
DELETE /api/glossary/1
```

**Пример ответа:**

```json
{
  "success": true,
  "message": "Термин успешно удален",
  "data": {
    "deleted_id": 1
  }
}
```

## Примеры использования с cURL

```bash
curl -X GET "http://localhost:8000/api/glossary" \
  -H "accept: application/json"

curl -X GET "http://localhost:8000/api/glossary/1" \
  -H "accept: application/json"


curl -X GET "http://localhost:8000/api/glossary/search/DeFi" \
  -H "accept: application/json"


curl -X POST "http://localhost:8000/api/glossary" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Мой новый термин",
    "definition": "Это определение моего нового термина с достаточно подробным описанием",
    "category": "Разработка",
    "examples": ["пример1"]
  }'


curl -X PUT "http://localhost:8000/api/glossary/1" \
  -H "Content-Type: application/json" \
  -d '{"definition": "Новое определение"}'

curl -X DELETE "http://localhost:8000/api/glossary/1" \
  -H "accept: application/json"
```

## Тестирование

```bash
pytest tests/ -v

pytest tests/test_api.py::TestCreateTerm -v

pytest tests/ --cov=app --cov-report=html
```

## Начальные данные

Глоссарий содержит 22 термина по теме разработки децентрализованных приложений:

**Основные концепции:**

- Децентрализованное приложение (DApp)
- Смарт-контракт

**Инфраструктура:**

- Блокчейн
- EVM (Ethereum Virtual Machine)
- Консенсус

**Приложения:**

- DeFi (Децентрализованные финансы)
- NFT (Non-Fungible Token)
- DEX (Децентрализованная биржа)
- DAO (Децентрализованная Автономная Организация)

**Инструменты:**

- Wallet (Кошелек)
- Web3.js
- ethers.js

**Программирование:**

- Solidity

**Финансовые концепции:**

- Gas (Газ)
- AMM (Automated Market Maker)
- Ликвидность
- Стейкинг

**И другие...**

## Валидация данных

Все входные данные проходят строгую валидацию через Pydantic модели:

```python
class GlossaryTermBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    definition: str = Field(..., min_length=10, max_length=2000)
    category: str = Field(default="General")
    examples: Optional[list[str]] = None
    related_terms: Optional[list[str]] = None
    source: Optional[str] = None
```

## Зависимости

- `fastapi==0.104.1` - Web фреймворк
- `uvicorn[standard]==0.24.0` - ASGI сервер
- `pydantic==2.5.0` - Валидация данных
- `pytest==7.4.3` - Тестирование

---
