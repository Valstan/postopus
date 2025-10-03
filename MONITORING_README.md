# 🚀 Автоматический мониторинг логов Render для Postopus

Система автоматического мониторинга логов деплоя на Render.com с уведомлениями о критических ошибках и фильтрацией по важности.

## 📋 Возможности

- ✅ **Автоматический мониторинг** логов во время деплоя
- 🚨 **Уведомления о критических ошибках** в реальном времени
- 🔍 **Фильтрация по важности** (критические, ошибки, предупреждения)
- 📊 **Детальная аналитика** проблем деплоя
- ⚡ **Быстрое обнаружение** ошибок типа `IndentationError`, `ImportError`
- 🎯 **Специализированный мониторинг** для сервисов Postopus

## 🛠️ Установка

Все скрипты готовы к использованию, дополнительные зависимости не требуются.

## 📖 Использование

### 1. Базовый мониторинг

```bash
# Мониторинг конкретного деплоя
python monitor_logs.py <service_id> <deploy_id> [max_wait_minutes]

# Пример
python monitor_logs.py srv-d3bv87r7mgec73a336s0 dep-d3g3ld49c44c73a8cgk0 15
```

### 2. Быстрый мониторинг

```bash
# Упрощенный запуск
python quick_monitor.py <service_id> <deploy_id> [max_wait_minutes]
```

### 3. Мониторинг с реальным MCP API

```bash
# Полноценный мониторинг через MCP Render API
python real_render_monitor.py <service_id> <deploy_id> [max_wait_minutes]
```

### 4. Мониторинг сервисов Postopus

```bash
# Показать все сервисы
python postopus_monitor.py list

# Мониторинг конкретного сервиса
python postopus_monitor.py monitor web

# Мониторинг всех сервисов
python postopus_monitor.py monitor-all

# Мониторинг с указанием ID деплоев
python postopus_monitor.py monitor-all web=dep-123 worker=dep-456
```

## 🎯 Сервисы Postopus

| Сервис | ID | Описание |
|--------|----|---------| 
| `web` | `srv-d3bv87r7mgec73a336s0` | Основной веб-интерфейс |
| `worker` | `srv-d3bv87r7mgec73a336s1` | Celery Worker |
| `scheduler` | `srv-d3bv87r7mgec73a336s2` | Celery Beat Scheduler |
| `redis` | `srv-d3bv87r7mgec73a336s3` | Redis для Celery |
| `postgres` | `srv-d3bv87r7mgec73a336s4` | PostgreSQL база данных |

## 🚨 Типы уведомлений

### Критические ошибки
- `IndentationError` - ошибки отступов
- `SyntaxError` - синтаксические ошибки
- `ImportError` - ошибки импорта модулей
- `ModuleNotFoundError` - модули не найдены
- `AttributeError` - ошибки атрибутов

### Ошибки сборки
- `build failed` - сбой сборки
- `installation failed` - ошибка установки
- `dependency error` - проблемы с зависимостями
- `pip error` - ошибки pip

### Ошибки приложения
- `connection refused` - отказ в соединении
- `database error` - ошибки базы данных
- `authentication failed` - ошибки аутентификации
- `port already in use` - порт занят

## 📊 Примеры вывода

### Успешный деплой
```
🔍 Начинаем мониторинг деплоя dep-d3g3ld49c44c73a8cgk0
📊 Сервис: srv-d3bv87r7mgec73a336s0
⏰ Максимальное время: 15 минут
================================================================================
📈 Статус деплоя: build_in_progress
ℹ️  ИНФО: [10:30:15] BUILD:INFO - Installing dependencies...
✅ УСПЕХ: [10:32:45] BUILD:INFO - Build successful
📈 Статус деплоя: live
🏁 Деплой завершен со статусом: live

================================================================================
📊 ФИНАЛЬНАЯ СВОДКА МОНИТОРИНГА
================================================================================
⏱️  Длительность: 0:02:30
🚨 Критические ошибки: 0
🔨 Предупреждения сборки: 0
🐛 Предупреждения приложения: 0
❌ Обычные ошибки: 0
⚠️  Предупреждения: 0
📈 Всего проблем: 0

✅ Деплой завершен успешно
```

### Деплой с ошибками
```
🚨 УВЕДОМЛЕНИЕ [CRITICAL] 🚨
⏰ Время: 2025-01-03 10:35:22
📊 Сервис: srv-d3bv87r7mgec73a336s0
🚀 Деплой: dep-d3g3ld49c44c73a8cgk0
📝 Сообщение: [10:35:22] BUILD:ERROR - IndentationError: unexpected indent
================================================================================

🚨 КРИТИЧЕСКИЕ ОШИБКИ:
  - [10:35:22] BUILD:ERROR - IndentationError: unexpected indent (line 189)

❌ Деплой завершен с 1 проблемами
```

## 🔧 Интеграция с MCP Render API

Система использует MCP Render API для получения логов в реальном времени:

```python
# Получение логов через MCP API
logs_response = mcp_render_list_logs(
    resource=[service_id],
    type=["build", "app"],
    limit=100,
    startTime=start_time.isoformat() + "Z",
    endTime=end_time.isoformat() + "Z",
    direction="backward"
)
```

## 🚀 Быстрый старт

1. **Мониторинг текущего деплоя:**
   ```bash
   python postopus_monitor.py monitor web
   ```

2. **Мониторинг всех сервисов:**
   ```bash
   python postopus_monitor.py monitor-all
   ```

3. **Мониторинг с кастомными параметрами:**
   ```bash
   python real_render_monitor.py srv-d3bv87r7mgec73a336s0 dep-123 20
   ```

## 📈 Преимущества

- ⚡ **Быстрое обнаружение** ошибок (в течение 30 секунд)
- 🎯 **Точная диагностика** проблем деплоя
- 📊 **Детальная аналитика** для оптимизации
- 🔔 **Автоматические уведомления** о критических проблемах
- 🛠️ **Простота использования** - один скрипт для всех задач

## 🔮 Планы развития

- [ ] Интеграция с Slack/Discord для уведомлений
- [ ] Email уведомления о критических ошибках
- [ ] Веб-интерфейс для мониторинга
- [ ] Автоматическое исправление простых ошибок
- [ ] Интеграция с CI/CD pipeline

## 📞 Поддержка

При возникновении проблем проверьте:
1. Правильность ID сервиса и деплоя
2. Доступность MCP Render API
3. Корректность формата команд

---

**Создано для проекта Postopus** 🚀
