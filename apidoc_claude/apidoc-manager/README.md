# APIDoc Manager CLI

```
 ___  ____  ____  ____  ____  ___       _  _   __   __ _   __    ___  ____  ____
/ __)( ___)(  _ \( ___)(_  _)/ __)     ( \/ ) / _\ (  ( \ / _\  / __)(  __)(  _ \
\__ \ )__)  )   / )__)   )(  \__ \      )  / /    \/    //    \( (_ \ ) _)  )   /
(___/(____)(__)\_)(____) (__) (___/ ____(__/  \_/\_/\_)__)\_/\_/ \___/(____)(__\_)
```

**CLI-инструмент для автоматизации работы с OpenAPI (Swagger) спецификациями.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-242%20passed-brightgreen)](#тестирование)
[![Coverage](https://img.shields.io/badge/coverage-83%25-green)](#тестирование)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

> Логотип: [docs/logo.svg](docs/logo.svg)

---

## Команды

| Команда | Описание |
|---------|----------|
| `apidoc generate` | Генерация спецификации из кода (FastAPI/Flask) или интерактивно |
| `apidoc validate` | Локальная + внешняя валидация, авто-исправления |
| `apidoc diff` | Сравнение версий, выявление breaking changes |
| `apidoc mock` | Mock-сервер из спецификации с логированием |
| `apidoc testgen` | Генерация pytest-тестов |
| `apidoc publish` | Публикация: собственный сервер + SwaggerHub, GitHub, GitLab, Redocly, ReadMe.com |
| `apidoc convert` | Конвертация форматов и версий OpenAPI |
| `apidoc tree` | ASCII-визуализация структуры API |
| `apidoc server` | Управление REST API сервером (9 подкоманд) |

---

## Установка

```bash
# Только основные зависимости (без dev-инструментов — быстро, для production)
pip install -e .

# С инструментами для разработки и тестирования
pip install -e ".[dev]"

# Автодополнение в терминале
apidoc --install-completion
```

---

## Быстрый старт

```bash
# 1. Инициализация БД и запуск сервера
apidoc server init
apidoc server start

# 2. Генерация спецификации из FastAPI-кода
apidoc generate ./app.py --output openapi.yaml

# 3. Валидация с авто-исправлениями
apidoc validate openapi.yaml --fix

# 4. Визуализация структуры
apidoc tree openapi.yaml

# 5. Публикация на сервер
apidoc publish openapi.yaml --server-only

# 6. Сравнение версий (для CI/CD)
apidoc diff old.yaml new.yaml --json --breaking-only

# 7. Mock-сервер для тестирования
apidoc mock openapi.yaml --port 8080

# 8. Генерация тестов
apidoc testgen openapi.yaml --output tests/

# 9. Публикация во внешние сервисы
apidoc publish openapi.yaml --target swaggerhub,github,gitlab,redocly,readme
```

---

## Конфигурация

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `APIDOC_SERVER_URL` | URL сервера | `http://localhost:8000` |
| `APIDOC_DB_URL` | URL БД | `sqlite:///~/.apidoc/data/apidoc.db` |
| `APIDOC_SWAGGERHUB_TOKEN` | API-ключ SwaggerHub | — |
| `APIDOC_SWAGGERHUB_OWNER` | Владелец в SwaggerHub | — |
| `APIDOC_GITHUB_TOKEN` | GitHub Personal Access Token | — |
| `APIDOC_GITHUB_REPO` | Репозиторий `owner/repo` | — |
| `APIDOC_GITLAB_TOKEN` | GitLab Personal Access Token | — |
| `APIDOC_GITLAB_PROJECT_ID` | ID проекта GitLab | — |
| `APIDOC_REDOCLY_TOKEN` | API-ключ Redocly | — |
| `APIDOC_README_TOKEN` | API-ключ ReadMe.com | — |
| `APIDOC_README_VERSION` | Ветка ReadMe.com | `stable` |

---

## REST API сервер

Запуск: `apidoc server start` → **http://localhost:8000**

- **Главная страница** (`/`) — интерактивная документация ReDoc со встроенным логотипом
- **Swagger UI** — `/docs`
- **ReDoc** — `/redoc`

### Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/specs` | Загрузка спецификации |
| GET | `/specs` | Список с пагинацией |
| GET | `/specs/{id}` | Получение по ID |
| DELETE | `/specs/{id}` | Удаление |
| GET | `/specs/search?q=` | Поиск по названию |
| POST | `/specs/import` | Импорт из URL |
| GET | `/specs/{id}/export` | Экспорт JSON/YAML |
| GET | `/specs/{id}/versions` | История версий |
| POST | `/specs/{id}/versions` | Новая версия |
| GET | `/specs/{id}/versions/{ver}` | Конкретная версия |
| POST | `/specs/{id}/diff` | Сравнение версий |
| GET | `/health` | Liveness check |
| GET | `/health/db` | Readiness check |
| GET | `/info` | Метаданные сервера |

---

## Внешние сервисы публикации

| Сервис | API | Аутентификация |
|--------|-----|----------------|
| SwaggerHub | `api.swaggerhub.com` | Token Header |
| GitHub | `api.github.com` | Bearer Token |
| GitLab | `gitlab.com/api/v4` | PRIVATE-TOKEN |
| Redocly | `app.redocly.com/api` | Bearer Token |
| **ReadMe.com** | `api.readme.com/v2` *(v2 API)* | Bearer Token |

> ReadMe.com использует **API v2** (Bearer Auth, hostname `api.readme.com`).

---

## Тестирование

```bash
# Все тесты (242 шт.)
pytest tests/ -v

# С отчётом о покрытии (83%)
pytest tests/ --cov=apidoc --cov=server --cov-report=html -q

# По уровням
pytest tests/unit/        -q   # 130 unit-тестов (быстро, без сети)
pytest tests/integration/ -q   # 82 интеграционных
pytest tests/e2e/         -q   # 30 end-to-end сценариев
```

---

## Структура проекта

```
apidoc-manager/
├── apidoc/
│   ├── cli.py                 # Точка входа (Typer, 9 команд)
│   ├── config.py              # Настройки из env-переменных
│   ├── commands/              # Вспомогательная логика команд
│   ├── api/
│   │   ├── client.py          # HTTP-клиент к собственному серверу
│   │   ├── validators.py      # Клиент OpenAPI Initiative Validator
│   │   └── publishers.py      # SwaggerHub, GitHub, GitLab, Redocly, ReadMe v2
│   ├── plugins/
│   │   ├── generators/        # FastAPI, Flask генераторы
│   │   └── testgens/          # pytest генератор тестов
│   └── utils/                 # errors (E001-E008), output (Rich), spec
├── server/
│   ├── main.py                # FastAPI + ReDoc главная страница
│   ├── models.py              # SQLAlchemy: Spec, SpecVersion
│   ├── schemas.py             # Pydantic схемы
│   ├── database.py            # Async SQLite/PostgreSQL engine
│   ├── routers/specs.py       # Все /specs эндпоинты
│   ├── services/spec_service.py # Бизнес-логика
│   └── migrations/            # Alembic миграции
├── tests/
│   ├── unit/                  # 130 тестов
│   ├── integration/           # 82 теста
│   └── e2e/                   # 30 тестов
├── docs/
│   └── logo.svg               # Анимированный SVG-логотип
├── LICENSE                    # MIT + ASCII-логотип
├── pyproject.toml
├── alembic.ini
└── README.md
```

---

## Коды ошибок

| Код | Тип | Описание |
|-----|-----|----------|
| E001 | NetworkError | Сервер недоступен или таймаут |
| E002 | AuthError | Неверный или отсутствующий API-ключ |
| E003 | ValidationError | Спецификация не прошла валидацию |
| E004 | ParseError | Невалидный YAML или JSON |
| E005 | NotFoundError | Ресурс не найден (404) |
| E006 | ServerError | Внутренняя ошибка сервера (5xx) |
| E007 | PluginError | Ошибка загрузки или выполнения плагина |
| E008 | ConfigError | Ошибка конфигурации |

---

## Лицензия

MIT © 2026 APIDoc Team — см. файл [LICENSE](LICENSE)
