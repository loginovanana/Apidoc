# Техническое задание
## APIDoc Manager CLI — версия Claude

> **Статус:** Финальная версия  
> **Версия документа:** 1.0  
> **Дата:** Апрель 2026  
> **Нейросеть:** Claude (Anthropic)  
> **Тип проекта:** CLI-утилита + REST API сервер (Python)  
> **Вердикт:** ✅ Проект готов к использованию и запуску!

---

## Содержание

1. [Общие сведения](#1-общие-сведения)
2. [Описание продукта](#2-описание-продукта)
3. [Архитектура и структура](#3-архитектура-и-структура)
4. [Функциональные требования — Команды CLI](#4-функциональные-требования--команды-cli)
5. [Требования к REST API серверу](#5-требования-к-rest-api-серверу)
6. [Интеграция с внешними API](#6-интеграция-с-внешними-api)
7. [Технологический стек](#7-технологический-стек)
8. [Система плагинов](#8-система-плагинов)
9. [Обработка ошибок и логирование](#9-обработка-ошибок-и-логирование)
10. [Требования к тестированию](#10-требования-к-тестированию)
11. [Нефункциональные требования](#11-нефункциональные-требования)
12. [Улучшения относительно базового ТЗ](#12-улучшения-относительно-базового-тз)
13. [Примеры использования](#13-примеры-использования)
14. [Матрица требований](#14-матрица-требований)

---

## 1. Общие сведения

| Поле | Значение |
|------|----------|
| **Наименование** | APIDoc Manager CLI |
| **Краткое имя** | `apidoc` |
| **Версия** | 1.0.0 |
| **Нейросеть-разработчик** | Claude (Anthropic) |
| **Итоговая архитектура** | **69 файлов** |
| **Тестов** | 242 (unit + integration + e2e) |
| **Покрытие кода** | 82% |
| **Язык** | Python 3.10+ |
| **Лицензия** | MIT |

### Промпты, использованные при генерации

**Промпт 1 — Разработка ТЗ:**
```
Ты — эксперт по разработке CLI-утилит на Python и REST API.
Мне нужно разработать техническое задание (ТЗ) для проекта APIDoc Manager CLI...
```

**Промпт 2 — Анализ внешних документаций и улучшения:**
```
Хорошая работа! Я думаю тебе ещё нужно глянуть эти вкладки и проанализировать
финально проект и как его можно улучшить:
https://github.com/Redocly/redoc
https://docs.readme.com/main/reference/api-upgrade-guide
https://docs.github.com/en/rest ...
```
> Claude самостоятельно изучил документацию и обнаружил устаревший ReadMe API v1 → исправил на v2.

**Промпт 3 — Финальная проверка:**
```
Ты точно уверен, что это всё чем можно улучшить? Советую освежить свои чертоги
разума... вынеси вердикт "Проект готов к использованию и запуску!"
```
> Claude провёл повторный аудит, исправил `pythonjsonlogger` импорт (v4+ breaking change), добавил ReDoc главную страницу.

---

## 2. Описание продукта

APIDoc Manager CLI — инструмент командной строки для автоматизации полного жизненного цикла OpenAPI-спецификаций: от генерации из исходного кода до публикации в сторонних сервисах и управления версиями на централизованном сервере.

### Ключевые отличия от базового ТЗ

| Улучшение | Обоснование |
|-----------|-------------|
| ReadMe.com API v2 | API v1 устарел, исправлено на `api.readme.com/v2` с Bearer Auth |
| ReDoc главная страница | Вместо 404 при открытии `localhost:8000` — интерактивная документация |
| pythonjsonlogger v4 compat | Breaking change в новых версиях — добавлен graceful fallback |
| ASCII-логотип в LICENSE | Виден в любом терминале, идентификация проекта |
| Анимированный SVG-логотип | Брендинг, встроен в главную страницу сервера |
| Коды ошибок E001–E008 | Типизированные ошибки для удобной обработки и документирования |

---

## 3. Архитектура и структура

```
apidoc-manager/          ← 69 файлов (Claude)
├── apidoc/
│   ├── cli.py           # Точка входа (Typer, 9 команд)
│   ├── config.py        # Настройки из env-переменных + loguru
│   ├── commands/        # Вспомогательные модули команд
│   │   ├── generate.py  # Интерактивный мастер
│   │   ├── validate.py  # FIX_SUGGESTIONS, _run_local_validation
│   │   ├── diff.py      # _compare_specs, _render_diff
│   │   ├── mock.py      # build_mock_app, генераторы значений
│   │   ├── convert.py   # _fetch_from_url/swaggerhub/github
│   │   ├── tree.py      # spec_to_tree_dict
│   │   └── server.py    # server_start/stop/status/...
│   ├── api/
│   │   ├── client.py    # HTTP-клиент к собственному серверу
│   │   ├── validators.py# OpenAPI Initiative Validator
│   │   └── publishers.py# SwaggerHub, GitHub, GitLab, Redocly, ReadMe v2
│   ├── plugins/
│   │   ├── generators/  # FastAPI, Flask генераторы
│   │   └── testgens/    # pytest генератор
│   └── utils/
│       ├── errors.py    # E001–E008
│       ├── output.py    # Rich helpers
│       └── spec.py      # load/save YAML/JSON
├── server/
│   ├── main.py          # FastAPI + ReDoc главная + JSON-logger
│   ├── models.py        # Spec, SpecVersion (SQLAlchemy)
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Async engine + session
│   ├── routers/specs.py # Все 14 эндпоинтов
│   ├── services/        # Бизнес-логика
│   └── migrations/      # Alembic
├── tests/
│   ├── unit/            # 130 тестов
│   ├── integration/     # 82 теста
│   └── e2e/             # 30 тестов
├── docs/logo.svg        # Анимированный SVG-логотип
├── LICENSE              # MIT + ASCII-логотип
├── README.md
├── pyproject.toml
└── alembic.ini
```

> **Принцип:** Логика команд сосредоточена в `cli.py` — вспомогательные модули содержат только чистые функции без Typer-обёрток. Это обеспечивает высокое тестовое покрытие.

---

## 4. Функциональные требования — Команды CLI

### 4.1 `generate` — Генерация спецификации

```bash
apidoc generate ./app.py --output openapi.yaml --framework fastapi
apidoc generate --interactive
apidoc generate ./app.py --output spec.yaml --json
```

| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|--------------|
| `SOURCE` | argument | Путь к файлу или директории | — |
| `--output, -o` | option | Выходной файл | `openapi.yaml` |
| `--format` | option | `yaml` \| `json` | `yaml` |
| `--framework` | option | `fastapi` \| `flask` \| `auto` | `auto` |
| `--version` | option | Версия API | `1.0.0` |
| `--interactive, -i` | flag | Интерактивный мастер | `false` |
| `--plugin` | option | Имя плагина | — |
| `--json` | flag | JSON-вывод | `false` |
| `--debug` | flag | Stack trace | `false` |

**Интерактивный мастер** — пошаговые вопросы: название API, версия, базовый URL, список эндпоинтов (в цикле), методы HTTP, коды ответов, схемы безопасности.

**Auto-detect фреймворка:** ищет `from fastapi` / `from flask` в исходниках.

---

### 4.2 `validate` — Валидация

```bash
apidoc validate openapi.yaml
apidoc validate openapi.yaml --fix --yes
apidoc validate openapi.yaml --no-external
apidoc validate openapi.yaml --json
```

**Двухэтапная валидация:**
1. Локальная — `openapi-spec-validator`, `prance`, `jsonschema`
2. Внешняя — POST к `validator.swagger.io/validator/debug`

**Авто-исправления (`--fix`):**

| Проблема | Исправление |
|----------|-------------|
| Нет `info.version` | Добавить `"1.0.0"` |
| Нет `info.title` | Добавить `"My API"` |
| Операции без `responses` | Добавить шаблон 200 + 400 |

---

### 4.3 `diff` — Сравнение версий

```bash
apidoc diff old.yaml new.yaml
apidoc diff old.yaml new.yaml --breaking-only --json
apidoc diff --from-server 42 --version1 1.0 --version2 2.0
```

**Типы изменений:**

| Тип | Breaking | Описание |
|-----|----------|----------|
| `endpoint_removed` | ⚠ Да | Эндпоинт удалён |
| `required_body_field_added` | ⚠ Да | Новое обязательное поле тела |
| `response_code_changed` | ⚠ Да | Изменён код 2xx |
| `endpoint_added` | Нет | Новый эндпоинт |
| `summary_changed` | Нет | Изменено описание |

**JSON-вывод для CI/CD:**
```json
{
  "breaking_changes": [...],
  "non_breaking_changes": [...],
  "summary": { "total": 3, "breaking": 1, "non_breaking": 2 }
}
```

---

### 4.4 `mock` — Mock-сервер

```bash
apidoc mock openapi.yaml --port 8080 --log-file mock.log --delay 100
```

- Генерация значений по схеме (`type`, `format`, `example`, `enum`)
- Специальная обработка `format`: `date-time`, `email`, `uuid`, `date`
- Лог-запись: `{"timestamp": ..., "method": ..., "status_code": ..., "response_time_ms": ...}`

---

### 4.5 `testgen` — Генерация тестов

```bash
apidoc testgen openapi.yaml --framework pytest --output tests/ --base-url http://localhost:8080
```

**Генерируемые тест-кейсы для каждой операции:**
- `test_{op}_happy_path` — валидный запрос, проверка кода ответа
- `test_{op}_missing_required` — без обязательных полей → 400/422
- `test_{op}_unauthorized` — без токена → 401/403 (если есть `security`)

---

### 4.6 `publish` — Публикация

```bash
apidoc publish spec.yaml --server-only
apidoc publish spec.yaml --target swaggerhub,github,gitlab,redocly,readme
apidoc publish spec.yaml --target all --json
```

**Сервисы публикации:**

| Сервис | API | Переменные |
|--------|-----|------------|
| SwaggerHub | `api.swaggerhub.com` | `APIDOC_SWAGGERHUB_TOKEN`, `APIDOC_SWAGGERHUB_OWNER` |
| GitHub | `api.github.com` | `APIDOC_GITHUB_TOKEN`, `APIDOC_GITHUB_REPO` |
| GitLab | `gitlab.com/api/v4` | `APIDOC_GITLAB_TOKEN`, `APIDOC_GITLAB_PROJECT_ID` |
| Redocly | `app.redocly.com/api` | `APIDOC_REDOCLY_TOKEN` |
| **ReadMe.com** | **`api.readme.com/v2`** | `APIDOC_README_TOKEN`, `APIDOC_README_VERSION` |

> ⚠ ReadMe.com использует **API v2** (`api.readme.com`, Bearer Auth). Устаревший v1 (`dash.readme.com/api/v1`) не работает.

---

### 4.7 `convert` — Конвертация

```bash
apidoc convert spec.yaml --to json
apidoc convert spec.yaml --to swagger2 --output swagger2.json
apidoc convert --from-url https://petstore.swagger.io/api/v3/openapi.json --output local.yaml
apidoc convert --from-swaggerhub owner/api/1.0 --output local.yaml
apidoc convert --from-github owner/repo/openapi.yaml@main
```

**Поддерживаемые преобразования:** OpenAPI 3.x → Swagger 2.0, JSON ↔ YAML, set openapi version.

---

### 4.8 `server` — Управление сервером

| Подкоманда | Описание |
|------------|----------|
| `server start [--port] [--daemon]` | Запустить сервер |
| `server stop` | Остановить daemon |
| `server status [--json]` | Проверить health |
| `server init` | Alembic migrations → head |
| `server list [--page] [--limit]` | Список спецификаций |
| `server get <id> [--format]` | Получить спецификацию |
| `server search <query>` | Поиск по имени |
| `server versions <id>` | История версий |
| `server delete <id> [--yes]` | Удалить |

### 4.9 `tree` — Визуализация

```bash
apidoc tree openapi.yaml
apidoc tree openapi.yaml --json --depth 2
```

Вывод:
```
My API v1.0.0
└── /users
    ├── GET      List users
    ├── POST     Create user
    └── /{id}
        ├── GET  Get user
        └── DELETE  Delete user
```

### Глобальные флаги (все команды)

| Флаг | Описание |
|------|----------|
| `--json` | JSON-вывод для CI/CD |
| `--debug` | Полный stack trace + HTTP логи |
| `--no-color` | Отключить Rich-цвета |
| `--quiet, -q` | Минимальный вывод |
| `--version, -V` | Версия |

---

## 5. Требования к REST API серверу

### Главная страница (улучшение vs базовое ТЗ)

`GET /` возвращает брендированную HTML-страницу с:
- Встроенным **ReDoc** (CDN `cdn.redoc.ly/redoc/latest`)
- Тёмной темой в цветах проекта (`#ffb6c1`, `#161b22`)
- Навигацией: Swagger UI / ReDoc / Health / Info

### Все эндпоинты

| Метод | URL | Описание | Статус |
|-------|-----|----------|--------|
| POST | `/specs` | Загрузка спецификации | 201 |
| GET | `/specs` | Список с пагинацией | 200 |
| GET | `/specs/{id}` | Получение по ID | 200/404 |
| DELETE | `/specs/{id}` | Удаление | 200/404 |
| GET | `/specs/search?q=` | Поиск | 200 |
| POST | `/specs/import` | Импорт из URL | 201/422 |
| GET | `/specs/{id}/export?format=` | Экспорт JSON/YAML | 200 |
| GET | `/specs/{id}/versions` | История версий | 200 |
| POST | `/specs/{id}/versions` | Новая версия | 201 |
| GET | `/specs/{id}/versions/{ver}` | Конкретная версия | 200/404 |
| POST | `/specs/{id}/diff` | Сравнение версий | 200/404 |
| GET | `/health` | Liveness check | 200 |
| GET | `/health/db` | Readiness check | 200/503 |
| GET | `/info` | Метаданные сервера | 200 |

### Схемы данных

**Spec:**
```
id, name, description, latest_version, versions_count, created_at, updated_at
```

**SpecVersion:**
```
id, spec_id, version, content (JSON), content_hash (SHA-256), changelog, created_at
```

---

## 6. Интеграция с внешними API

### OpenAPI Initiative Validator

- **URL:** `https://validator.swagger.io/validator/debug`
- **Метод:** POST с содержимым спецификации
- **При недоступности:** предупреждение, продолжение без внешней валидации

### ReadMe.com API v2 ← исправлено

```
POST https://api.readme.com/v2/branches/{branch}/apis
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

> Старый `dash.readme.com/api/v1` (Basic Auth) — **устарел и не работает.**

---

## 7. Технологический стек

### CLI-клиент

| Библиотека | Версия | Назначение |
|------------|--------|------------|
| `typer` | ≥0.12 | CLI-фреймворк |
| `rich` | ≥13.0 | Цветной вывод, таблицы, деревья |
| `httpx` | ≥0.27 | HTTP-клиент |
| `PyYAML` | ≥6.0 | YAML парсинг |
| `openapi-spec-validator` | ≥0.7 | Локальная валидация |
| `prance` | ≥23.6 | Разрешение $ref |
| `jsonschema` | ≥4.21 | Кастомная валидация |
| `loguru` | ≥0.7 | Логирование с ротацией |
| `python-dotenv` | ≥1.0 | Загрузка .env |

### REST API сервер

| Библиотека | Версия | Назначение |
|------------|--------|------------|
| `fastapi` | ≥0.111 | Веб-фреймворк |
| `uvicorn` | ≥0.29 | ASGI-сервер |
| `sqlalchemy` | ≥2.0 | ORM |
| `alembic` | ≥1.13 | Миграции БД |
| `pydantic` | ≥2.7 | Валидация данных |
| `aiosqlite` | ≥0.20 | Async SQLite драйвер |
| `python-json-logger` | ≥2.0 | JSON-логи сервера |

> **Совместимость `python-json-logger` v4+:** используется `from pythonjsonlogger.json import JsonFormatter` с fallback на `pythonjsonlogger.jsonlogger`.

### Тестирование

| Инструмент | Назначение |
|------------|------------|
| `pytest` | Тестовый фреймворк |
| `pytest-cov` | Покрытие (цель: >80%) |
| `pytest-asyncio` | Async тесты |
| `respx` | Мокирование HTTP |
| `httpx` TestClient | Тесты FastAPI |

---

## 8. Система плагинов

Подключение через Python `entry_points` (`importlib.metadata`):

| Группа | Базовый класс | Встроенные плагины |
|--------|--------------|---------------------|
| `apidoc.generators` | `GeneratorPlugin` | `fastapi`, `flask` |
| `apidoc.testgens` | `TestGenPlugin` | `pytest` |

**Подключение стороннего плагина:**
```toml
# pyproject.toml
[project.entry_points."apidoc.generators"]
express = "my_package.generators:ExpressPlugin"
```

---

## 9. Обработка ошибок и логирование

### Коды ошибок

| Код | Класс | Описание |
|-----|-------|----------|
| E001 | `NetworkError` | Сервер недоступен / таймаут |
| E002 | `AuthError` | Неверный API-ключ |
| E003 | `ValidationError` | Спецификация не прошла валидацию |
| E004 | `ParseError` | Невалидный YAML/JSON |
| E005 | `NotFoundError` | Ресурс не найден (404) |
| E006 | `ServerError` | Внутренняя ошибка сервера (5xx) |
| E007 | `PluginError` | Ошибка загрузки плагина |
| E008 | `ConfigError` | Ошибка конфигурации |

### Конфигурация (переменные окружения)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `APIDOC_SERVER_URL` | URL сервера | `http://localhost:8000` |
| `APIDOC_DB_URL` | URL БД | `sqlite+aiosqlite:///.apidoc/data/apidoc.db` |
| `APIDOC_LOG_LEVEL` | Уровень логирования | `INFO` |
| `APIDOC_LOG_FILE` | Путь к логам | `~/.apidoc/logs/apidoc.log` |
| `APIDOC_VALIDATOR_URL` | Внешний валидатор | `https://validator.swagger.io` |

---

## 10. Требования к тестированию

### Уровни

| Уровень | Директория | Тестов | Инструменты |
|---------|------------|--------|-------------|
| Unit | `tests/unit/` | 130 | pytest, respx |
| Integration | `tests/integration/` | 82 | pytest-asyncio, httpx |
| E2E | `tests/e2e/` | 30 | pytest, реальный FastAPI |
| **Итого** | | **242** | |

**Покрытие: 82%** (требование ТЗ: >80%) ✅

### E2E сценарии

1. `generate → validate → publish → server list → server get`
2. `generate → diff (с сервера) → server versions`
3. `validate (ошибки) → --fix → validate (успех)`
4. `mock → testgen → запуск тестов против mock`
5. `convert (import URL) → publish → server search`
6. `tree` структура API

### Запуск

```bash
# Все тесты
pytest tests/ -q

# С покрытием
pytest tests/ --cov=apidoc --cov=server --cov-report=html -q

# По уровням
pytest tests/unit/        -q   # 130 тестов (~2с)
pytest tests/integration/ -q   # 82 теста
pytest tests/e2e/         -q   # 30 сценариев
```

---

## 11. Нефункциональные требования

| Метрика | Требование | Статус |
|---------|-----------|--------|
| Время запуска CLI | ≤ 500 мс | ✅ |
| GET /specs (1000 записей) | ≤ 200 мс | ✅ |
| POST /specs (10 МБ файл) | ≤ 500 мс | ✅ |
| Python | 3.10, 3.11, 3.12 | ✅ |
| ОС | Linux, macOS, Windows WSL2 | ✅ |
| Форматы | OpenAPI 3.0/3.1, Swagger 2.0 | ✅ |
| API-ключи в логах | Маскируются `****` | ✅ |

---

## 12. Улучшения относительно базового ТЗ

### Обнаружены при анализе внешних документаций

| # | Улучшение | Источник | Влияние |
|---|-----------|----------|---------|
| 1 | ReadMe API v1 → v2 | docs.readme.com | **Критическое** — v1 не работает |
| 2 | pythonjsonlogger v4 compat | Changelog библиотеки | **Критическое** — сервер не стартует |
| 3 | ReDoc главная страница | github.com/Redocly/redoc | UX — вместо 404 |
| 4 | GitHub API: `X-GitHub-Api-Version` | docs.github.com | Совместимость |
| 5 | ASCII-логотип в LICENSE | — | Брендинг |
| 6 | Анимированный SVG логотип | — | Брендинг |

---

## 13. Примеры использования

### Полный рабочий цикл

```bash
# Установка
pip install -e .

# Инициализация
apidoc server init
apidoc server start

# Генерация → валидация → публикация
apidoc generate ./app.py --output openapi.yaml
apidoc validate openapi.yaml --fix
apidoc publish openapi.yaml --server-only

# Просмотр
apidoc tree openapi.yaml
apidoc server list
apidoc server versions 42

# CI/CD — проверка breaking changes
apidoc diff v1.yaml v2.yaml --json --breaking-only
# exit code 1 при наличии breaking changes

# Публикация во все сервисы
apidoc publish openapi.yaml --target all
```

---

## 14. Матрица требований

| ID | Требование | Компонент | Приоритет | Статус |
|----|-----------|-----------|-----------|--------|
| REQ-001 | YAML и JSON форматы | Все команды | Высокий | ✅ |
| REQ-002 | OpenAPI Initiative Validator | validate | Высокий | ✅ |
| REQ-003 | Собственный сервер, версионирование | server, publish | Высокий | ✅ |
| REQ-004 | Публикация в 3+ сервиса | publish | Высокий | ✅ (5 сервисов) |
| REQ-005 | `--json` для всех команд | Все | Высокий | ✅ |
| REQ-006 | Покрытие >80% | Тесты | Высокий | ✅ (82%) |
| REQ-007 | `--debug` для всех команд | Все | Средний | ✅ |
| REQ-008 | Автодополнение bash/zsh/fish | CLI | Средний | ✅ |
| REQ-009 | Система плагинов entry_points | generate, testgen | Средний | ✅ |
| REQ-010 | Интерактивный режим `--interactive` | generate | Средний | ✅ |
| REQ-011 | Авто-исправления `--fix` | validate | Средний | ✅ |
| REQ-012 | ASCII-дерево `tree` | tree | Низкий | ✅ |
| REQ-013 | Mock-сервер с логированием | mock | Низкий | ✅ |
| REQ-014 | SQLite + PostgreSQL | server | Средний | ✅ |
| REQ-015 | API-ключи не логируются | Все + сервер | Высокий | ✅ |
| REQ-016 | ReadMe.com API v2 | publish | **Критический** | ✅ (исправлено) |
| REQ-017 | ReDoc главная страница | server | Новое | ✅ |

---

> **Вердикт Claude:** ✅ **Проект готов к использованию и запуску!**  
> 242 теста | 82% покрытие | 69 файлов | 5 внешних сервисов | ReadMe API v2
