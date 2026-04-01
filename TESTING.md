# 🧪 Тестирование Postopus

Проект использует два типа тестов: **unit-тесты** и **интеграционные тесты**.

## 📋 Структура тестов

### Unit-тесты (безопасные для CI/CD)

Расположены в папке `tests/` и **не требуют** подключения к MongoDB или VK API:

| Файл | Что тестирует | Тесты |
|------|---------------|-------|
| `tests/test_env_loader.py` | Загрузка конфигурации, TEST_POLYGON, session dict | 11 тестов |
| `tests/test_posting_post.py` | Логика редиректа в тестовый полигон | 5 тестов |
| `tests/test_start_cli.py` | Парсинг CLI аргументов (в т.ч. `--test`) | 9 тестов |
| `tests/test_driver_tables_no_mongo.py` | Fallback при отсутствии MongoDB | 1 тест |
| `tests/test_session_parser.py` | Загрузка региональной сессии, парсер | 2 теста |
| **Итого** | **Быстрые, чистые тесты** | **28 тестов** ✅ |

**Запуск unit-тестов:**
```bash
pytest tests/
# или
pytest tests/ -v  # подробный вывод
# или
pytest tests/ -k test_cli  # конкретный набор тестов
```

### Интеграционные тесты (требуют реального окружения)

Расположены в корне проекта:

| Файл | Что делает | Требует |
|------|-----------|---------|
| `test_start_paket_integration.py` | Полный цикл парсинга + постинга для всех 15 регионов | MongoDB, VK токены, 15+ минут |

⚠️ **Не запускать в CI/CD!** Этот тест дорогой в смысле времени и потребляет токены.

**Запуск интеграционного теста (только локально):**
```bash
python test_start_paket_integration.py  # интерактивный режим
python test_start_paket_integration.py mi_novost  # тестировать только novost во всех регионах
```

---

## 🎯 Новые фичи тестирования

### 1. Флаг `--test` для CLI

Быстро тестировать постинг в **тестовый полигон** без редактирования `.env`:

```bash
# Нормальный режим (в рабочие группы)
python start.py mi_novost

# Тестовый режим (в полигон -137760500)
python start.py mi_novost --test

# С количеством bag'ов и флагом
python start.py mi_novost 1 --test
```

### 2. Переменная окружения `TEST_POLYGON_MODE`

В файле `.env`:
```env
TEST_POLYGON_MODE=true   # Все публикации идут в полигон
# или
TEST_POLYGON_MODE=1      # Альтернативный формат
# или оставить пусто / false для обычного режима
```

### 3. Тестовый полигон (Test Polygon)

- **ID сообщества:** -137760500
- **URL:** https://vk.com/ititenskoegore
- **Логирование:** При активном режиме логируется `logger.info("Redirecting post...")`

---

## ✅ Статус CI/CD

**GitHub Actions workflow** (`.github/workflows/ci.yml`):
- Запускается на push в ветку `old_postopus`
- Запускает `pytest tests/ -q` (только unit-тесты)
- Python 3.12
- **Результат:** ✅ Быстро (10–15 сек), безопасно (нет токенов), надёжно

---

## 🚀 Примеры использования

### Сценарий 1: Развитие новой фичи

```bash
# Делаешь правку в коде (например, в parser.py)
# 1. Запускаешь unit-тесты локально
pytest tests/ -v

# 2. Если нужна интеграция, запускаешь один регион
python start.py mi_novost --test

# 3. Коммитишь и пушишь — GitHub Actions автоматически запустит tests/
git add bin/control/parser.py
git commit -m "Fix parser logic"
git push origin old_postopus
```

### Сценарий 2: Отладка публикаций

```bash
# Публикуешь в тестовый полигон для быстрой проверки
python start.py mi_novost --test

# Проверяешь результат в https://vk.com/ititenskoegore
# Логи покажут: "Redirecting post for session 'novost' ... to TEST_POLYGON_GROUP_ID -137760500"
```

### Сценарий 3: CI/CD проверка перед merge

```bash
# GitHub Actions автоматически:
# 1. Проверит синтаксис Python
# 2. Запустит 28 unit-тестов
# 3. Выдаст зелёный галочку или красный крест
# Нет потребления токенов, очень быстро ✅
```

---

## 📊 Результаты локального запуска

```
============================= test session starts ==============================
platform win32 -- Python 3.12.7, pytest-9.0.2
collected 27 items

tests/test_driver_tables_no_mongo.py::test_load_table_returns_default_when_no_mongo PASSED [ 3%]
tests/test_env_loader.py::test_test_polygon_group_id_is_numeric PASSED      [ 7%]
tests/test_env_loader.py::test_session_dict_exists PASSED                   [11%]
tests/test_env_loader.py::test_session_has_required_keys PASSED             [14%]
... (всего 27 тестов, 10 секунд)

============================== 27 passed in 10.19s ==============================
```

---

## 🔧 Как добавить новый тест

1. Создай файл `tests/test_my_feature.py`
2. Используй `unittest.mock` для изоляции от real API/DB
3. Запусти: `pytest tests/test_my_feature.py -v`
4. Коммитом добавь в тесты

**Пример:**
```python
from unittest.mock import patch

def test_my_function():
    with patch('module.external_api') as mock_api:
        mock_api.return_value = {'status': 'ok'}
        result = my_function()
        assert result is True
```

---

## ⚡ Быстрые команды

```bash
# Все unit-тесты
pytest tests/

# Один конкретный файл тестов
pytest tests/test_start_cli.py

# Один конкретный тест
pytest tests/test_start_cli.py::test_start_py_cli_with_test_flag

# С покрытием (coverage)
pytest tests/ --cov=bin --cov=env_loader

# Тесты, которые содержат "test" в имени
pytest tests/ -k "test"
```

---

**Последнее обновление:** 2026-04-01  
**Ответственный:** AI-ассистент Postopus  
**Статус:** ✅ Протестировано и готово к использованию
