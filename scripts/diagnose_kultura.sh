#!/bin/bash
# Диагностика постинга kultura — собирает всё за один запуск
# Запуск: cd /home/valstan/postopus && bash scripts/diagnose_kultura.sh

set -e

echo "============================================================"
echo "🔍 ДИАГНОСТИКА ПОСТИНГА KULTURA"
echo "============================================================"
echo ""

cd /home/valstan/postopus

# Обновляем код
echo "📥 Обновляем код..."
git pull --quiet 2>/dev/null || echo "⚠️ git pull не удался, продолжаем..."
echo ""

# Запускаем kultura и сохраняем полный вывод
LOGFILE="/tmp/kultura_diagnose_$(date +%Y%m%d_%H%M%S).log"
echo "🚀 Запускаем start_paket.py kultura..."
echo "   Лог сохраняется в: $LOGFILE"
echo ""

/usr/bin/python3 start_paket.py kultura 2>&1 | tee "$LOGFILE"

echo ""
echo "============================================================"
echo "📊 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ"
echo "============================================================"
echo ""

# 1. Итоговая статистика постинга
echo "═══ 1. СТАТИСТИКА ПОСТИНГА (из Тестового полигона) ═══"
grep -E "(Успешно|Неудачи|Всего постов|ПРОШЕЛ|ИТОГО)" "$LOGFILE" | tail -20 || echo "   (не найдено)"
echo ""

# 2. Свежие посты по регионам
echo "═══ 2. СВЕЖИЕ ПОСТЫ (прошли sort_old_date) ═══"
grep "Свежий пост прошел sort_old_date" "$LOGFILE" | wc -l | xargs -I{} echo "   Найдено {} свежих постов"
echo ""
echo "   По регионам:"
grep "Свежий пост прошел sort_old_date" "$LOGFILE" | sed 's/.*📰 //' | sed 's/ |.*//' | sort | uniq -c | sort -rn | head -20
echo ""

# 3. Отброшенные посты
echo "═══ 3. ОТБРОШЕННЫЕ ПОСТЫ ═══"
grep "❌ Свежий пост отброшен" "$LOGFILE" | wc -l | xargs -I{} echo "   Отброшено {} постов"
echo ""
echo "   Причины отсева:"
grep "❌ Свежий пост отброшен" "$LOGFILE" | sed 's/.*(\(.*\)): .*/\1/' | sort | uniq -c | sort -rn
echo ""

# 4. Прошедшие все фильтры
echo "═══ 4. ПРОШЕДШИЕ ВСЕ ФИЛЬТРЫ ═══"
grep "ПРОШЕЛ ВСЕ ФИЛЬТРЫ" "$LOGFILE" | wc -l | xargs -I{} echo "   Прошло {} постов"
grep "ПРОШЕЛ ВСЕ ФИЛЬТРЫ" "$LOGFILE" | head -10 || echo "   (нет)"
echo ""

# 5. Ошибки
echo "═══ 5. ОШИБКИ ═══"
grep -iE "(Error|Traceback|Exception|KeyError|'novost')" "$LOGFILE" | head -20 || echo "   Ошибок не найдено"
echo ""

# 6. Итоговая сводка фильтрации по каждому региону
echo "═══ 6. ИТОГО ФИЛЬТРАЦИЯ (по регионам) ═══"
grep "ИТОГО ФИЛЬТРАЦИЯ" "$LOGFILE" || echo "   (не найдено — возможно код на сервере старый)"
echo ""

# 7. Проблемные регионы из статистики
echo "═══ 7. ПРОБЛЕМНЫЕ РЕГИОНЫ (из статистики) ═══"
grep "•.*Инфо:" "$LOGFILE" | grep -A0 "Нет свежих\|novost\|logger\|Error" | head -20 || echo "   (не найдено)"
echo ""

echo "============================================================"
echo "📁 ПОЛНЫЙ ЛОГ: $LOGFILE"
echo "============================================================"
