# APIDoc Manager CLI
## Отчёт о разработке с использованием нейросетей

```
 ___  ____  ____  ____  ____  ___       _  _   __   __ _   __    ___  ____  ____
/ __)( ___)(  _ \( ___)(_  _)/ __)     ( \/ ) / _\ (  ( \ / _\  / __)(  __)(  _ \
\__ \ )__)  )   / )__)   )(  \__ \      )  / /    \/    //    \( (_ \ ) _)  )   /
(___/(____)(__)\_)(____) (__) (___/ ____(__/  \_/\_/\_)__)\_/\_/ \___/(____)(__\_)
                    CLI for OpenAPI Specification Management
```

> **Учебный проект** | Магистратура | Программирование на Python | 2026  
> **Задача:** Реализовать CLI-утилиту с помощью двух нейросетей на основе одинаковых промптов и сравнить результаты

---

## Содержание

1. [О проекте](#1-о-проекте)
2. [Использованные промпты](#2-использованные-промпты)
3. [Быстрый старт — Claude версия](#3-быстрый-старт--claude-версия)
4. [Сравнение нейросетей](#4-сравнение-нейросетей)
5. [Структура архивов](#5-структура-архивов)
6. [Команды CLI](#6-команды-cli)
7. [Тестирование](#7-тестирование)
8. [Скриншоты](#8-скриншоты)
9. [Итоги и выводы](#9-итоги-и-выводы)
10. [Лицензия](#10-лицензия)

---

## 1. О проекте

**APIDoc Manager CLI** — инструмент командной строки для автоматизации работы с OpenAPI (Swagger) спецификациями. Позволяет:

- **Генерировать** OpenAPI-спецификации из исходного кода (FastAPI, Flask) или интерактивно
- **Валидировать** спецификации через локальную проверку и официальный OpenAPI Initiative Validator
- **Сравнивать** версии и выявлять breaking changes для CI/CD
- **Публиковать** в 5 внешних сервисах: SwaggerHub, GitHub, GitLab, Redocly, ReadMe.com
- **Хранить и версионировать** через собственный FastAPI REST API сервер
- **Генерировать тесты** и запускать mock-серверы

### Документы проекта

| Файл | Описание |
|------|----------|
| [`TZ_Claude.md`](TZ_Claude.md) | Техническое задание — версия Claude |
| [`TZ_DeepSeek.md`](TZ_DeepSeek.md) | Техническое задание — версия DeepSeek |
| [`README_Report.md`](README_Report.md) | Данный отчёт |
| [`docs/logo.svg`](docs/logo.svg) | Анимированный SVG-логотип |
| [`LICENSE`](LICENSE) | MIT лицензия с ASCII-логотипом |

---

## 2. Использованные промпты

Оба инструмента получали **идентичные промпты** в одинаковой последовательности.

---

### Промпт 1 — Разработка технического задания

```
Ты — эксперт по разработке CLI-утилит на Python и REST API.
Мне нужно разработать техническое задание (ТЗ) для проекта
APIDoc Manager CLI — инструмента командной строки для
автоматизации работы с OpenAPI (Swagger) спецификациями.

[Описание инструмента, функциональные требования, технологический
стек, примеры использования — полный текст задания]

Минимальное количество команд: 8 основных команд
(generate, validate, diff, mock, testgen, publish, convert, server)
```

**Результат:**
- Claude → сгенерировал ТЗ и оформил в `.docx` с таблицами через библиотеку docx
- DeepSeek → сгенерировал структурированный текстовый ТЗ

---

### Промпт 2 — Анализ внешних документаций и улучшение

```
Хорошая работа! Я думаю тебе ещё нужно глянуть эти вкладки
и проанализировать финально проект и как его можно улучшить:

https://github.com/Redocly/redoc
https://docs.swagger.io/spec.html
https://docs.readme.com/main/reference/api-upgrade-guide
https://docs.github.com/en/rest
https://www.geeksforgeeks.org/git/github-rest-api/
```

**Результат:**
- Claude → самостоятельно обнаружил устаревший ReadMe.com API v1, исправил на v2; нашёл breaking change в `pythonjsonlogger`; предложил ReDoc главную страницу
- DeepSeek → предложил улучшения, но не обнаружил критические баги с API

---

### Промпт 3 — Финальная верификация

```
Ты точно уверен, что это всё чем можно улучшить и ничем
не можешь его дополнить? То есть передаешь мне код и подтверждаешь,
что он рабочий и будет соответствовать ТЗ, а также исправно работать
при первой сборке без критических багов. Если нет, то советую
освежить свои чертоги разума и точно в этом удостовериться,
дополни архив и вынеси вердикт:
"Проект готов к использованию и запуску!"
```

**Результат:**
- Claude → провёл повторный аудит, исправил 2 критических бага, добавил брендинг, вынес вердикт ✅
- DeepSeek → подтвердил готовность, но часть багов осталась

---

## 3. Быстрый старт — Claude версия

> Это готовая к запуску версия. Распакуйте архив и выполните команды ниже.

### Установка

```bash
cd apidoc-manager
pip install -e .
```

### Инициализация и запуск сервера

```bash
# Создать базу данных
apidoc server init

# Запустить сервер (первый терминал)
apidoc server start
```

Откройте браузер: **http://localhost:8000** — ReDoc с документацией API.

### Основные команды (второй терминал)

```bash
# Проверить версию
apidoc --version

# Создать тестовый файл
cat > app.py << 'EOF'
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def list_users(): return []

@app.post("/users")
def create_user(): return {}

@app.get("/users/{user_id}")
def get_user(user_id: int): return {}
EOF

# Сгенерировать спецификацию
apidoc generate app.py --output openapi.yaml

# Посмотреть структуру
apidoc tree openapi.yaml

# Валидировать с авто-исправлениями
apidoc validate openapi.yaml --fix

# Опубликовать на сервер
apidoc publish openapi.yaml --server-only

# Список спецификаций
apidoc server list

# Сравнить версии
apidoc diff openapi.yaml openapi.yaml --json

# Mock-сервер
apidoc mock openapi.yaml --port 8080

# Генерация тестов
apidoc testgen openapi.yaml --output my_tests/
```

### Конфигурация внешних сервисов

Создайте файл `.env` в папке проекта:

```env
# SwaggerHub
APIDOC_SWAGGERHUB_TOKEN=your-token
APIDOC_SWAGGERHUB_OWNER=your-username

# GitHub
APIDOC_GITHUB_TOKEN=ghp_your_token
APIDOC_GITHUB_REPO=username/repo

# GitLab
APIDOC_GITLAB_TOKEN=glpat-your-token
APIDOC_GITLAB_PROJECT_ID=12345

# Redocly
APIDOC_REDOCLY_TOKEN=your-token

# ReadMe.com (API v2)
APIDOC_README_TOKEN=your-token
APIDOC_README_VERSION=stable
```

```bash
# Публикация во все сервисы
apidoc publish openapi.yaml --target swaggerhub,github,gitlab,redocly,readme
```

---

## 4. Сравнение нейросетей

### Общие метрики

| Метрика | 🔵 DeepSeek | 🌸 Claude |
|---------|-------------|-----------|
| Файлов в проекте | **118** | **69** |
| Первый запуск без правок | ❌ Нет | ✅ Да |
| Способ получения кода | Файлы в диалоге (вручную) | Готовый .zip архив |
| Сборка структуры | Ручная (переименовать, разложить) | Автоматическая |
| Количество правок до запуска | Много | Минимум |
| Тестов | Есть (покрытие не указано) | **242 теста, 82%** |
| Обнаружен баг ReadMe API v1→v2 | ❌ | ✅ самостоятельно |
| Обнаружен баг pythonjsonlogger | ❌ | ✅ самостоятельно |
| Главная страница сервера | 404 | ✅ ReDoc |
| ASCII-логотип в LICENSE | ❌ | ✅ |
| Анимированный SVG-логотип | ✅ (другой стиль) | ✅ |

---

### Детальное сравнение

| Критерий | 🔵 DeepSeek | 🌸 Claude | Победитель |
|----------|-------------|-----------|-----------|
| **Получение кода** | Файлы в диалоге, ручная сборка | Zip-архив — распаковал и запустил | 🌸 Claude |
| **Первый запуск** | Требовалось много правок | Работало с первого раза | 🌸 Claude |
| **Архитектура** | 118 файлов — подробная декомпозиция | 69 файлов — лаконично | 🌸 Claude |
| **Доступность для новичка** | Нужен опыт Python, знание структуры | Понятно без опыта Python | 🌸 Claude |
| **Тестирование** | Есть, покрытие не измерено | 242 теста, 82% coverage | 🌸 Claude |
| **Актуальность API** | ReadMe v1 (устарело) | ReadMe v2 (актуально) | 🌸 Claude |
| **Изучение архитектуры** | Подробная слоевая декомпозиция | Более компактная структура | 🔵 DeepSeek |
| **Логотип** | Создан (разный стиль — вкусовщина) | Создан (разный стиль — вкусовщина) | 🤝 Ничья |
| **ТЗ** | Текстовый документ | Текст + оформленный .docx | 🌸 Claude |

---

### Когда что использовать

**DeepSeek — выбирайте, если:**
- Хотите изучить архитектуру по частям
- Нужна детальная декомпозиция с пояснениями
- Есть опыт Python и не боитесь собирать структуру вручную
- Интересует enterprise-паттерны (repository pattern, отдельные schemas)

**Claude — выбирайте, если:**
- Нужен результат «распаковал и запустил»
- Нет опыта Python или времени на отладку
- Важна актуальность внешних API
- Нужно высокое тестовое покрытие из коробки

---

## 5. Структура архивов

### Claude версия (69 файлов)

```
apidoc-manager/
├── apidoc/
│   ├── cli.py                 ← точка входа, 9 команд
│   ├── config.py              ← env-переменные, loguru
│   ├── commands/              ← вспомогательная логика
│   │   ├── generate.py        ← интерактивный мастер
│   │   ├── validate.py        ← FIX_SUGGESTIONS
│   │   ├── diff.py            ← _compare_specs
│   │   ├── mock.py            ← build_mock_app
│   │   ├── convert.py         ← импорт из URL/SwaggerHub/GitHub
│   │   ├── tree.py            ← spec_to_tree_dict
│   │   └── server.py          ← server_start/stop/list/...
│   ├── api/
│   │   ├── client.py          ← HTTP-клиент к серверу (14 эндпоинтов)
│   │   ├── validators.py      ← OpenAPI Initiative Validator
│   │   └── publishers.py      ← 5 сервисов, ReadMe v2
│   ├── plugins/
│   │   ├── generators/        ← FastAPI, Flask
│   │   └── testgens/          ← pytest
│   └── utils/
│       ├── errors.py          ← E001–E008
│       ├── output.py          ← Rich helpers
│       └── spec.py            ← load/save YAML/JSON
├── server/
│   ├── main.py                ← FastAPI + ReDoc главная
│   ├── models.py              ← Spec, SpecVersion (SQLAlchemy)
│   ├── schemas.py             ← Pydantic
│   ├── database.py            ← async SQLite/PostgreSQL
│   ├── routers/specs.py       ← 14 эндпоинтов
│   ├── services/spec_service.py
│   └── migrations/            ← Alembic
├── tests/
│   ├── unit/                  ← 130 тестов
│   ├── integration/           ← 82 теста
│   └── e2e/                   ← 30 сценариев
├── docs/logo.svg              ← анимированный SVG
├── LICENSE                    ← MIT + ASCII-логотип
├── README.md
├── pyproject.toml
└── alembic.ini
```

### DeepSeek версия (118 файлов)

```
apidoc-manager/
├── apidoc/
│   ├── commands/              ← отдельные Typer-приложения
│   ├── api/                   ← HTTP-клиенты
│   ├── models/                ← модели данных CLI
│   ├── schemas/               ← схемы валидации CLI
│   ├── repositories/          ← паттерн Repository
│   ├── plugins/               ← система плагинов
│   ├── utils/                 ← утилиты
│   └── config/                ← конфигурация
├── server/
│   ├── routers/               ← роутеры
│   ├── services/              ← сервисный слой
│   ├── repositories/          ← слой БД
│   ├── models/                ← ORM модели
│   ├── schemas/               ← Pydantic (отдельно от CLI)
│   └── migrations/            ← Alembic
├── tests/
├── docs/
├── scripts/                   ← вспомогательные скрипты
└── docker/                    ← Docker-конфигурация
```

> DeepSeek использует паттерн Repository (отдельный слой между сервисом и БД) и разделяет схемы для CLI и сервера. Это увеличивает количество файлов, но даёт более чёткое разделение ответственности.

---

## 6. Команды CLI

### Полный список

```bash
apidoc --version                                    # версия
apidoc --help                                       # справка

# Генерация
apidoc generate ./app.py --output openapi.yaml
apidoc generate --interactive                       # мастер
apidoc generate ./app.py --json                    # JSON-вывод

# Валидация
apidoc validate openapi.yaml
apidoc validate openapi.yaml --fix --yes           # авто-исправление
apidoc validate openapi.yaml --no-external         # только локально
apidoc validate openapi.yaml --json                # JSON-вывод
apidoc validate openapi.yaml --debug               # stack trace

# Сравнение версий
apidoc diff v1.yaml v2.yaml
apidoc diff v1.yaml v2.yaml --breaking-only
apidoc diff v1.yaml v2.yaml --json                 # для CI/CD
apidoc diff --from-server 42 --version1 1.0 --version2 2.0

# Mock-сервер
apidoc mock openapi.yaml --port 8080
apidoc mock openapi.yaml --log-file mock.log
apidoc mock openapi.yaml --delay 100               # задержка 100мс

# Генерация тестов
apidoc testgen openapi.yaml --output tests/
apidoc testgen openapi.yaml --base-url http://localhost:8080

# Публикация
apidoc publish openapi.yaml --server-only
apidoc publish openapi.yaml --target swaggerhub,github
apidoc publish openapi.yaml --target all
apidoc publish openapi.yaml --json                 # JSON-отчёт

# Конвертация
apidoc convert openapi.yaml --to json
apidoc convert openapi.yaml --to swagger2
apidoc convert --from-url https://example.com/api.yaml --output local.yaml
apidoc convert --from-swaggerhub owner/api/1.0

# Дерево API
apidoc tree openapi.yaml
apidoc tree openapi.yaml --json

# Управление сервером
apidoc server init                                  # инициализация БД
apidoc server start                                 # запустить
apidoc server start --port 9000 --daemon           # в фоне
apidoc server stop                                  # остановить
apidoc server status                               # статус
apidoc server list                                  # список спецификаций
apidoc server list --page 2 --limit 10
apidoc server get 42                               # получить по ID
apidoc server get 42 --format json
apidoc server search payment                       # поиск
apidoc server versions 42                          # история версий
apidoc server delete 42 --yes                      # удалить
```

### Глобальные флаги

Применимы ко **всем** командам:

| Флаг | Описание |
|------|----------|
| `--json` | Вывод в JSON для CI/CD и скриптов |
| `--debug` | Полный stack trace + HTTP-логи всех запросов |
| `--no-color` | Отключить цветной вывод Rich |
| `--quiet, -q` | Только результат, без информационных сообщений |

---

## 7. Тестирование

### Запуск

```bash
# Установка зависимостей
pip install -e ".[dev]"

# Все тесты
pytest tests/ -v

# Быстро — только unit (без сети, без сервера)
pytest tests/unit/ -q

# Интеграционные (тестируют FastAPI через httpx)
pytest tests/integration/ -q

# E2E сценарии
pytest tests/e2e/ -q

# С отчётом о покрытии
pytest tests/ --cov=apidoc --cov=server --cov-report=term -q

# HTML-отчёт (открыть htmlcov/index.html)
pytest tests/ --cov=apidoc --cov=server --cov-report=html -q

# Конкретный тест или модуль
pytest tests/unit/commands/test_generate.py -v
pytest tests/integration/test_server_specs.py::TestCreateSpec -v
pytest tests/e2e/test_e2e_scenarios.py::TestE2EGenerateValidate -v
```

### Результаты (Claude версия)

| Уровень | Файл | Тестов | Покрытие |
|---------|------|--------|----------|
| Unit — утилиты | `tests/unit/test_utils.py` | 22 | ✅ |
| Unit — помощники команд | `tests/unit/test_commands_helpers.py` | 40 | ✅ |
| Unit — generate | `tests/unit/commands/test_generate.py` | 11 | ✅ |
| Unit — validate | `tests/unit/commands/test_validate.py` | 9 | ✅ |
| Unit — diff | `tests/unit/commands/test_diff.py` | 8 | ✅ |
| Unit — convert | `tests/unit/commands/test_convert.py` | 7 | ✅ |
| Unit — testgen | `tests/unit/commands/test_testgen.py` | 8 | ✅ |
| Unit — wizard | `tests/unit/commands/test_generate_wizard.py` | 7 | ✅ |
| Unit — API client | `tests/unit/api/test_client.py` | 10 | ✅ |
| Unit — publishers | `tests/unit/api/test_publishers.py` | 8 | ✅ |
| Unit — validators | `tests/unit/api/test_validators.py` | 5 | ✅ |
| Unit — publishers ext | `tests/unit/api/test_publishers_extended.py` | 8 | ✅ |
| Integration — сервер | `tests/integration/test_server_specs.py` | 34 | ✅ |
| Integration — сервис | `tests/integration/test_service_layer.py` | 28 | ✅ |
| Integration — CLI+сервер | `tests/integration/cli/test_cli_server.py` | 20 | ✅ |
| E2E — сценарии | `tests/e2e/test_e2e_scenarios.py` | 17 | ✅ |
| **Итого** | | **242** | **82%** |

---

## 8. Скриншоты

> Вставьте скриншоты в разделы ниже после запуска проекта.

### 8.1 Терминал — запуск сервера

```
[ СКРИНШОТ: apidoc server init && apidoc server start ]
```

---

### 8.2 Браузер — главная страница http://localhost:8000

```
[ СКРИНШОТ: ReDoc с логотипом, тёмная тема, навигация: Swagger UI / ReDoc / Health / Info ]
```

---

### 8.3 Браузер — http://localhost:8000/docs (Swagger UI)

```
[ СКРИНШОТ: список всех 14 эндпоинтов в Swagger UI ]
```

---

### 8.4 Терминал — команда generate

```
[ СКРИНШОТ: apidoc generate app.py --output openapi.yaml ]
Ожидаемый вывод:
ℹ Generating from app.py…
✓ Spec generated → openapi.yaml (3 endpoint(s))
```

---

### 8.5 Терминал — команда tree

```
[ СКРИНШОТ: apidoc tree openapi.yaml ]
Ожидаемый вывод:
My App API v1.0.0
└── /users
    ├── GET      List users
    ├── POST     Create user
    └── /{user_id}
        └── GET  Get user by ID
```

---

### 8.6 Терминал — команда validate --fix

```
[ СКРИНШОТ: apidoc validate openapi.yaml --fix ]
Ожидаемый вывод:
Fix: Missing info.version — Add info.version: "1.0.0"? [Y/n]:
✓ Applied fix: Missing info.version
✓ Spec is valid!
```

---

### 8.7 Терминал — команда diff с breaking changes

```
[ СКРИНШОТ: apidoc diff v1.yaml v2.yaml ]
Ожидаемый вывод:
Diff summary: 1 breaking / 1 non-breaking / 2 total

Changes
└── ⚠ Breaking Changes
    └── ✗ Endpoint removed: POST /users
  Non-Breaking Changes
    └── + New endpoint: GET /users/bulk
```

---

### 8.8 Терминал — запуск тестов с покрытием

```
[ СКРИНШОТ: pytest tests/ --cov=apidoc --cov=server -q ]
Ожидаемый вывод:
242 passed, 10 warnings in 8.17s
TOTAL  82%
```

---

### 8.9 Логотип проекта (docs/logo.svg)

```
[ СКРИНШОТ или вставить SVG напрямую в презентацию ]
Файл: docs/logo.svg
Цвета: #ffb6c1 (основной), #cfcfcf, #6699cc, #cc8800
```

---

### 8.10 DeepSeek vs Claude — сборка проекта

```
[ СКРИНШОТ: диалог DeepSeek — файлы выводятся в чат ]
[ СКРИНШОТ: Claude — ссылка на скачивание .zip архива ]
```

---

## 9. Итоги и выводы

### Ответ на вопрос презентации

> «APIDoc. Какой doc выберешь ты?»

```bash
$ apidoc generate ./my_life.py --output career.yaml
✓ Документация пишет себя. Вы — нет.
```

---

### Главные выводы

**1. Обе нейросети справились с задачей создания CLI-утилиты**  
Оба инструмента сгенерировали рабочий код со всеми требуемыми командами, REST API сервером, тестами и документацией.

**2. Разница — в опыте пользователя, а не в качестве кода**  
DeepSeek пишет подробнее и детальнее, но результат требует ручной сборки. Claude даёт готовый к запуску архив.

**3. Claude лучше для пользователей без Python-опыта**  
Zip-архив + одна команда `pip install -e .` + инструкция = работающий проект. DeepSeek требует понимания структуры Python-проектов.

**4. Claude самостоятельно нашёл критические баги**  
ReadMe API v1 → v2 и `pythonjsonlogger` breaking change были обнаружены без подсказки — только по результатам анализа внешней документации.

**5. Размер != качество**  
118 файлов DeepSeek — не лучше и не хуже 69 файлов Claude. Это разные архитектурные подходы: enterprise-декомпозиция vs прагматичная компактность.

---

### Итоговый счёт

| Категория | 🔵 DeepSeek | 🌸 Claude |
|-----------|:-----------:|:---------:|
| Первый запуск без правок | ❌ | ✅ |
| Готовый архив для скачивания | ❌ | ✅ |
| Актуальные внешние API | ❌ | ✅ |
| Доступность без Python-опыта | ❌ | ✅ |
| Тестовое покрытие измерено | ✅84% | ✅ 82% |
| Брендинг (логотип, LICENSE) | ➖ | ✅ |
| Детальная архитектурная декомпозиция | ✅ | ➖ |
| Подходит для изучения паттернов | ✅ | ➖ |
| **Итого** | **3 / 8** | **6 / 8** |

---

## 10. Лицензия

```
MIT License
Copyright (c) 2026 APIDoc Team

 ___  ____  ____  ____  ____  ___       _  _   __   __ _   __    ___  ____  ____
/ __)( ___)(  _ \( ___)(_  _)/ __)     ( \/ ) / _\ (  ( \ / _\  / __)(  __)(  _ \
\__ \ )__)  )   / )__)   )(  \__ \      )  / /    \/    //    \( (_ \ ) _)  )   /
(___/(____)(__)\_)(____) (__) (___/ ____(__/  \_/\_/\_)__)\_/\_/ \___/(____)(__\_)
```

Полный текст: [LICENSE](LICENSE)

---

*Проект выполнен в рамках учебного курса «Программирование на Python»*  
*Магистратура · Второй семестр · 2026*
