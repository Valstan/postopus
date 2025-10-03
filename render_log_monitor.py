#!/usr/bin/env python3
"""
Интеграция с MCP Render API для автоматического мониторинга логов
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
import os

# Добавляем путь к MCP модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class RenderLogMonitor:
    """Монитор логов Render через MCP API"""
    
    def __init__(self, service_id: str, deploy_id: str):
        self.service_id = service_id
        self.deploy_id = deploy_id
        self.last_log_timestamp = None
        self.processed_logs = set()  # Для избежания дублирования
        
    async def get_deploy_status(self) -> Optional[str]:
        """Получает статус деплоя через MCP API"""
        try:
            # Здесь будет реальный вызов MCP Render API
            # Пока возвращаем симуляцию
            return "build_in_progress"
        except Exception as e:
            print(f"❌ Ошибка получения статуса деплоя: {e}")
            return None
    
    async def get_recent_logs(self, log_type: str = "app", limit: int = 50) -> List[Dict]:
        """Получает последние логи через MCP API"""
        try:
            # Здесь будет реальный вызов MCP Render API
            # mcp_render_list_logs(resource=[self.service_id], type=[log_type], limit=limit)
            
            # Пока возвращаем симуляцию
            return []
        except Exception as e:
            print(f"❌ Ошибка получения логов: {e}")
            return []
    
    async def get_build_logs(self) -> List[Dict]:
        """Получает логи сборки"""
        return await self.get_recent_logs("build", 100)
    
    async def get_app_logs(self) -> List[Dict]:
        """Получает логи приложения"""
        return await self.get_recent_logs("app", 100)
    
    def analyze_log_severity(self, log: Dict) -> str:
        """Анализирует серьезность лога"""
        message = log.get("message", "").lower()
        level = log.get("level", "info").lower()
        
        # Критические ошибки
        critical_keywords = [
            "traceback", "exception", "fatal", "critical",
            "indentationerror", "syntaxerror", "importerror",
            "modulenotfounderror", "attributerror", "nameerror"
        ]
        
        if any(keyword in message for keyword in critical_keywords):
            return "critical"
        
        # Ошибки сборки
        build_error_keywords = [
            "build failed", "installation failed", "dependency error",
            "pip error", "package not found", "version conflict"
        ]
        
        if log.get("type") == "build" and any(keyword in message for keyword in build_error_keywords):
            return "build_error"
        
        # Ошибки приложения
        app_error_keywords = [
            "connection refused", "database error", "authentication failed",
            "permission denied", "file not found", "port already in use"
        ]
        
        if log.get("type") == "app" and any(keyword in message for keyword in app_error_keywords):
            return "app_error"
        
        # Обычные уровни
        if level in ["error", "err"]:
            return "error"
        elif level in ["warning", "warn"]:
            return "warning"
        elif level in ["info", "information"]:
            return "info"
        else:
            return "debug"
    
    def format_log_message(self, log: Dict) -> str:
        """Форматирует сообщение лога для вывода"""
        timestamp = log.get("timestamp", "")
        level = log.get("level", "info")
        message = log.get("message", "")
        log_type = log.get("type", "app")
        
        # Форматируем timestamp
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%H:%M:%S")
            except:
                formatted_time = timestamp
        else:
            formatted_time = "??:??:??"
        
        return f"[{formatted_time}] {log_type.upper()}:{level.upper()} - {message}"
    
    async def monitor_deployment_realtime(self, max_wait_minutes: int = 15):
        """Мониторинг деплоя в реальном времени"""
        print(f"🔍 Начинаем мониторинг деплоя {self.deploy_id}")
        print(f"📊 Сервис: {self.service_id}")
        print(f"⏰ Максимальное время: {max_wait_minutes} минут")
        print("=" * 80)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=max_wait_minutes)
        
        critical_issues = []
        build_issues = []
        app_issues = []
        
        while datetime.now() < end_time:
            try:
                # Проверяем статус деплоя
                status = await self.get_deploy_status()
                if status:
                    print(f"📈 Статус деплоя: {status}")
                    
                    if status in ["live", "update_failed", "build_failed"]:
                        print(f"🏁 Деплой завершен со статусом: {status}")
                        break
                
                # Получаем логи сборки
                build_logs = await self.get_build_logs()
                for log in build_logs:
                    log_id = f"{log.get('timestamp', '')}_{log.get('message', '')}"
                    if log_id not in self.processed_logs:
                        self.processed_logs.add(log_id)
                        
                        severity = self.analyze_log_severity(log)
                        formatted_msg = self.format_log_message(log)
                        
                        if severity == "critical":
                            print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА: {formatted_msg}")
                            critical_issues.append(log)
                        elif severity == "build_error":
                            print(f"🔨 ОШИБКА СБОРКИ: {formatted_msg}")
                            build_issues.append(log)
                        elif severity == "error":
                            print(f"❌ ОШИБКА: {formatted_msg}")
                        elif severity == "warning":
                            print(f"⚠️  ПРЕДУПРЕЖДЕНИЕ: {formatted_msg}")
                        elif "successful" in log.get("message", "").lower():
                            print(f"✅ УСПЕХ: {formatted_msg}")
                        else:
                            print(f"ℹ️  ИНФО: {formatted_msg}")
                
                # Получаем логи приложения
                app_logs = await self.get_app_logs()
                for log in app_logs:
                    log_id = f"{log.get('timestamp', '')}_{log.get('message', '')}"
                    if log_id not in self.processed_logs:
                        self.processed_logs.add(log_id)
                        
                        severity = self.analyze_log_severity(log)
                        formatted_msg = self.format_log_message(log)
                        
                        if severity == "critical":
                            print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА: {formatted_msg}")
                            critical_issues.append(log)
                        elif severity == "app_error":
                            print(f"🐛 ОШИБКА ПРИЛОЖЕНИЯ: {formatted_msg}")
                            app_issues.append(log)
                        elif severity == "error":
                            print(f"❌ ОШИБКА: {formatted_msg}")
                        elif severity == "warning":
                            print(f"⚠️  ПРЕДУПРЕЖДЕНИЕ: {formatted_msg}")
                
                # Ждем перед следующей проверкой
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                print("\n🛑 Мониторинг остановлен пользователем")
                break
            except Exception as e:
                print(f"❌ Ошибка мониторинга: {e}")
                await asyncio.sleep(10)
        
        # Финальная сводка
        duration = datetime.now() - start_time
        total_issues = len(critical_issues) + len(build_issues) + len(app_issues)
        
        print("\n" + "=" * 80)
        print("📊 СВОДКА МОНИТОРИНГА")
        print("=" * 80)
        print(f"⏱️  Длительность: {duration}")
        print(f"🚨 Критические ошибки: {len(critical_issues)}")
        print(f"🔨 Ошибки сборки: {len(build_issues)}")
        print(f"🐛 Ошибки приложения: {len(app_issues)}")
        print(f"📈 Всего проблем: {total_issues}")
        
        if critical_issues:
            print("\n🚨 КРИТИЧЕСКИЕ ОШИБКИ:")
            for issue in critical_issues:
                print(f"  - {self.format_log_message(issue)}")
        
        if build_issues:
            print("\n🔨 ОШИБКИ СБОРКИ:")
            for issue in build_issues:
                print(f"  - {self.format_log_message(issue)}")
        
        if app_issues:
            print("\n🐛 ОШИБКИ ПРИЛОЖЕНИЯ:")
            for issue in app_issues:
                print(f"  - {self.format_log_message(issue)}")
        
        return {
            "critical_issues": critical_issues,
            "build_issues": build_issues,
            "app_issues": app_issues,
            "total_issues": total_issues,
            "duration": str(duration)
        }

async def main():
    """Главная функция"""
    if len(sys.argv) < 3:
        print("Использование: python render_log_monitor.py <service_id> <deploy_id> [max_wait_minutes]")
        print("Пример: python render_log_monitor.py srv-d3bv87r7mgec73a336s0 dep-d3g3ld49c44c73a8cgk0 15")
        sys.exit(1)
    
    service_id = sys.argv[1]
    deploy_id = sys.argv[2]
    max_wait = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    
    monitor = RenderLogMonitor(service_id, deploy_id)
    result = await monitor.monitor_deployment_realtime(max_wait)
    
    # Возвращаем код выхода в зависимости от результата
    if result["total_issues"] > 0:
        print(f"\n❌ Деплой завершен с {result['total_issues']} проблемами")
        sys.exit(1)
    else:
        print(f"\n✅ Деплой завершен успешно")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
