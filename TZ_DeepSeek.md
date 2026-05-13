# Техническое задание
## APIDoc Manager CLI — версия DeepSeek

> **Статус:** Draft  
> **Версия:** 1.0  
> **Дата:** Апрель 2026  
> **Нейросеть:** DeepSeek  
> **Тип проекта:** CLI-утилита + REST API сервер (Python)

---

## Содержание

1. [Общие сведения](#1-общие-сведения)
2. [Описание продукта](#2-описание-продукта)
3. [Состав системы](#3-состав-системы)
4. [Функциональные требования — Команды CLI](#4-функциональные-требования--команды-cli)
5. [Требования к REST API серверу](#5-требования-к-rest-api-серверу)
6. [Технологический стек](#6-технологический-стек)
7. [Обработка ошибок и логирование](#7-обработка-ошибок-и-логирование)
8. [Требования к тестированию](#8-требования-к-тестированию)
9. [Примеры использования](#9-примеры-использования)
10. [Нефункциональные требования](#10-нефункциональные-требования)

---

## 1. Общие сведения

| Поле | Значение |
|------|----------|
| **Наименование** | APIDoc Manager CLI |
| **Краткое имя** | `apidoc` |
| **Версия** | 1.0.0 |
| **Нейросеть-разработчик** | DeepSeek |
| **Итоговая архитектура** | **118 файлов** |
| **Язык** | Python 3.10+ |

### Промпты, использованные при генерации ТЗ

**Промпт 1 — Основной:**
```
Ты — эксперт по разработке CLI-утилит на Python и REST API.
Мне нужно разработать техническое задание (ТЗ) для проекта APIDoc Manager CLI...
[полный текст промпта из задания]
```

**Промпт 2 — Анализ и улучшение:**
```
Хорошая работа! Я думаю тебе ещё нужно глянуть эти вкладки и проанализировать
финально проект и как его можно улучшить...
```

**Промпт 3 — Финальная проверка:**
```
Ты точно уверен, что это всё чем можно улучшить? То есть передаешь мне код
и подтверждаешь, что он рабочий...
```

---

## 2. Описание продукта

APIDoc Manager CLI — инструмент командной строки для автоматизации работы с OpenAPI-спецификациями. Позволяет генерировать документацию из исходного кода, проверять её корректность, сравнивать версии и создавать тесты на основе спецификации.

### Цели разработки

- Автоматизация генерации OpenAPI-спецификаций из кода
- Валидация спецификаций с предложением исправлений
- Управление версиями через собственный REST API сервер
- Публикация в 3+ внешних сервисах
- Генерация тестов и запуск mock-серверов

---

## 3. Состав системы

```
apidoc-manager/          ← 118 файлов (DeepSeek)
├── apidoc/              # CLI-клиент
│   ├── commands/        # Команды (отдельные модули)
│   ├── api/             # HTTP-клиенты
│   ├── plugins/         # Система плагинов
│   ├── utils/           # Утилиты
│   ├── models/          # Модели данных
│   ├── schemas/         # Схемы валидации
│   └── config/          # Конфигурация
├── server/              # FastAPI сервер
│   ├── routers/         # Роутеры
│   ├── services/        # Сервисный слой
│   ├── repositories/    # Слой работы с БД
│   ├── models/          # ORM-модели
│   ├── schemas/         # Pydantic-схемы
│   └── migrations/      # Alembic
├── tests/               # Тесты
├── docs/                # Документация
├── scripts/             # Вспомогательные скрипты
└── docker/              # Docker-конфигурация
```

> **Особенность DeepSeek:** Детальная декомпозиция по слоям (repository pattern, отдельные schemas/models для CLI и сервера). Архитектура более enterprise-ориентирована, что обусловило 118 файлов.

---

## 4. Функциональные требования — Команды CLI

### 4.1 Команда `generate`

```bash
apidoc generate [SOURCE] [OPTIONS]
apidoc generate ./app.py --output openapi.yaml --framework fastapi
apidoc generate --interactive
apidoc generate ./app.py --output spec.yaml --json
```

| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|--------------|
| `SOURCE` | argument | Путь к файлу или директории | — |
| `--output, -o` | option | Путь к выходному файлу | `openapi.yaml` |
| `--format` | option | Формат: `json` \| `yaml` | `yaml` |
| `--framework` | option | `fastapi` \| `flask` \| `auto` | `auto` |
| `--interactive, -i` | flag | Интерактивный режим | `false` |
| `--plugin` | option | Имя плагина | — |
| `--json` | flag | JSON-вывод для CI/CD | `false` |
| `--debug` | flag | Полный stack trace | `false` |

**Поддерживаемые фреймворки:** FastAPI, Flask, Express.js, Spring Boot, Gin (Go) — через плагины.

---

### 4.2 Команда `validate`

```bash
apidoc validate openapi.yaml
apidoc validate openapi.yaml --fix
apidoc validate openapi.yaml --debug
```

| Параметр | Описание |
|----------|----------|
| `--fix` | Предлагать авто-исправления |
| `--strict` | Предупреждения как ошибки |
| `--debug` | Полный stack trace |
| `--json` | JSON-вывод |

**Логика валидации:**
1. Локальная проверка (синтаксис, структура, `$ref`)
2. Внешняя проверка через `validator.swagger.io`

---

### 4.3 Команда `diff`

```bash
apidoc diff old.yaml new.yaml
apidoc diff old.yaml new.yaml --json --breaking-only
apidoc diff --from-server 123 --version1=1.0 --version2=1.1
```

**Категории изменений:**

| Тип | Breaking? |
|-----|-----------|
| Удалён эндпоинт | ⚠ Да |
| Добавлен обязательный параметр | ⚠ Да |
| Изменён тип поля | ⚠ Да |
| Добавлен новый эндпоинт | Нет |
| Изменено описание | Нет |

---

### 4.4 Команда `mock`

```bash
apidoc mock openapi.yaml --port 8080 --log-file mock.log
```

- Генерация ответов по `example` или `schema`
- Логирование: timestamp, method, path, status_code, response_time_ms

---

### 4.5 Команда `testgen`

```bash
apidoc testgen openapi.yaml --framework pytest --output tests/
```

Для каждой операции генерируются: happy path, negative, auth тесты.

---

### 4.6 Команда `publish`

```bash
apidoc publish spec.yaml --target swaggerhub,github,redocly
apidoc publish spec.yaml --target all
```

**Поддерживаемые сервисы:**

| Сервис | Переменная окружения |
|--------|---------------------|
| SwaggerHub | `APIDOC_SWAGGERHUB_TOKEN` |
| GitHub | `APIDOC_GITHUB_TOKEN` |
| GitLab | `APIDOC_GITLAB_TOKEN` |
| Redocly | `APIDOC_REDOCLY_TOKEN` |
| ReadMe.com | `APIDOC_README_TOKEN` |

---

### 4.7 Команда `convert`

```bash
apidoc convert spec.yaml --to json
apidoc convert --from-url https://example.com/api.yaml --output local.yaml
```

Поддержка: OpenAPI 3.0 ↔ 3.1 ↔ Swagger 2.0, JSON ↔ YAML.

---

### 4.8 Команда `server`

| Подкоманда | Описание |
|------------|----------|
| `server start` | Запустить сервер |
| `server stop` | Остановить сервер |
| `server status` | Проверить статус |
| `server init` | Инициализация БД |
| `server list` | Список спецификаций |
| `server get <id>` | Получить по ID |
| `server search <q>` | Поиск |
| `server versions <id>` | История версий |
| `server delete <id>` | Удалить |

---

## 5. Требования к REST API серверу

### Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/specs` | Загрузка спецификации |
| GET | `/specs` | Список с пагинацией |
| GET | `/specs/{id}` | Получение по ID |
| DELETE | `/specs/{id}` | Удаление |
| GET | `/specs/search?q=` | Поиск |
| POST | `/specs/import` | Импорт из URL |
| GET | `/specs/{id}/export` | Экспорт |
| GET | `/specs/{id}/versions` | История версий |
| POST | `/specs/{id}/versions` | Новая версия |
| POST | `/specs/{id}/diff` | Сравнение версий |
| GET | `/health` | Health check |
| GET | `/info` | Информация о сервере |

### База данных

- **По умолчанию:** SQLite
- **Опционально:** PostgreSQL (через `APIDOC_DB_URL`)
- **Миграции:** Alembic

---

## 6. Технологический стек

### CLI-клиент

```
typer>=0.12        Rich>=13.0        httpx>=0.27
PyYAML>=6.0        openapi-spec-validator>=0.7
prance>=23.6       jsonschema>=4.21   loguru>=0.7
python-dotenv>=1.0
```

### REST API сервер

```
fastapi>=0.111     uvicorn>=0.29     sqlalchemy>=2.0
alembic>=1.13      pydantic>=2.7     aiosqlite>=0.20
python-json-logger>=2.0
```

### Тестирование

```
pytest>=8.0        pytest-cov>=5.0   pytest-asyncio>=0.23
```

---

## 7. Обработка ошибок и логирование

| Код | Тип | Поведение |
|-----|-----|-----------|
| E001 | NetworkError | Сообщение + совет проверить URL |
| E002 | AuthError | Инструкция по env-переменной |
| E003 | ValidationError | Список ошибок + предложение --fix |
| E004 | ParseError | Строка и символ ошибки |
| E005 | NotFoundError | Сообщение + проверить ID |
| E006 | ServerError | Совет проверить логи сервера |
| E007 | PluginError | Имя + причина |
| E008 | ConfigError | Путь к конфиг. файлу |

**Логирование:** `~/.apidoc/logs/apidoc.log` — ротация 50 МБ, хранение 30 дней.

---

## 8. Требования к тестированию

| Уровень | Цель |
|---------|------|
| Unit-тесты | >80% покрытия каждого модуля |
| Integration | Все эндпоинты сервера |
| E2E | Критические пользовательские сценарии |

---

## 9. Примеры использования

```bash
# Генерация из FastAPI-кода
apidoc generate ./app.py --output=openapi.yaml --json

# Интерактивное создание
apidoc generate --interactive

# Публикация в 3 сервиса
apidoc publish spec.yaml --target=swaggerhub,github,redocly

# Визуализация API
apidoc tree spec.yaml

# Отладка
apidoc validate broken.yaml --debug

# Поиск на сервере
apidoc server search payment

# Сравнение версий с сервера
apidoc diff --from-server 123 --version1=1.0 --version2=1.1
```

---

## 10. Нефункциональные требования

| Метрика | Требование |
|---------|-----------|
| Время запуска CLI | ≤ 500 мс |
| Ответ сервера (GET) | ≤ 200 мс |
| Python | 3.10, 3.11, 3.12 |
| ОС | Linux, macOS, Windows (WSL2) |
| Форматы | OpenAPI 3.0.x, 3.1.x, Swagger 2.0 |

---

> **Итог DeepSeek:** Архитектура из 118 файлов с детальной слоевой декомпозицией (repository pattern, отдельные модели для CLI и сервера). Файлы генерируются в диалоге и требуют ручной сборки структуры проекта перед запуском.
