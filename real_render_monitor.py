#!/usr/bin/env python3
"""
Интеграция с реальным MCP Render API для мониторинга логов
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
import os

# Импортируем MCP функции (если доступны)
try:
    # Эти функции будут доступны в контексте MCP
    from mcp_render_list_logs import mcp_render_list_logs
    from mcp_render_get_deploy import mcp_render_get_deploy
    from mcp_render_get_service import mcp_render_get_service
except ImportError:
    # Заглушки для тестирования
    def mcp_render_list_logs(*args, **kwargs):
        return {"logs": [], "hasMore": False}
    
    def mcp_render_get_deploy(*args, **kwargs):
        return {"status": "build_in_progress"}
    
    def mcp_render_get_service(*args, **kwargs):
        return {"status": "live"}

class RealRenderMonitor:
    """Реальный монитор логов Render через MCP API"""
    
    def __init__(self, service_id: str, deploy_id: str):
        self.service_id = service_id
        self.deploy_id = deploy_id
        self.last_log_timestamp = None
        self.processed_log_ids = set()
        
    async def get_deploy_status(self) -> Optional[str]:
        """Получает реальный статус деплоя"""
        try:
            deploy_info = mcp_render_get_deploy(
                serviceId=self.service_id,
                deployId=self.deploy_id
            )
            return deploy_info.get("status", "unknown")
        except Exception as e:
            print(f"❌ Ошибка получения статуса деплоя: {e}")
            return None
    
    async def get_recent_logs(self, log_type: str = "app", limit: int = 50) -> List[Dict]:
        """Получает реальные логи через MCP API"""
        try:
            # Получаем логи за последние 5 минут
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)
            
            logs_response = mcp_render_list_logs(
                resource=[self.service_id],
                type=[log_type],
                limit=limit,
                startTime=start_time.isoformat() + "Z",
                endTime=end_time.isoformat() + "Z",
                direction="backward"
            )
            
            return logs_response.get("logs", [])
            
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
        
        # Критические ошибки Python
        critical_python_errors = [
            "indentationerror", "syntaxerror", "importerror",
            "modulenotfounderror", "attributerror", "nameerror",
            "typeerror", "valueerror", "keyerror", "indexerror"
        ]
        
        # Критические ошибки сборки
        critical_build_errors = [
            "build failed", "installation failed", "dependency error",
            "pip error", "package not found", "version conflict",
            "compilation failed", "make error"
        ]
        
        # Критические ошибки приложения
        critical_app_errors = [
            "connection refused", "database error", "authentication failed",
            "permission denied", "file not found", "port already in use",
            "out of memory", "disk full", "service unavailable"
        ]
        
        # Проверяем критические ошибки
        all_critical = critical_python_errors + critical_build_errors + critical_app_errors
        if any(keyword in message for keyword in all_critical):
            return "critical"
        
        # Ошибки сборки
        if log.get("type") == "build" and any(keyword in message for keyword in [
            "warning", "deprecated", "outdated", "version mismatch"
        ]):
            return "build_warning"
        
        # Ошибки приложения
        if log.get("type") == "app" and any(keyword in message for keyword in [
            "timeout", "retry", "fallback", "degraded"
        ]):
            return "app_warning"
        
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
        """Форматирует сообщение лога"""
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
    
    def should_notify(self, severity: str, log: Dict) -> bool:
        """Определяет, нужно ли отправить уведомление"""
        if severity == "critical":
            return True
        
        # Уведомления для ошибок сборки
        if severity == "build_warning" and log.get("type") == "build":
            return True
        
        # Уведомления для ошибок приложения
        if severity == "app_warning" and log.get("type") == "app":
            return True
        
        return False
    
    async def send_notification(self, severity: str, log: Dict):
        """Отправляет уведомление о проблеме"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = self.format_log_message(log)
        
        print(f"\n🚨 УВЕДОМЛЕНИЕ [{severity.upper()}] 🚨")
        print(f"⏰ Время: {timestamp}")
        print(f"📊 Сервис: {self.service_id}")
        print(f"🚀 Деплой: {self.deploy_id}")
        print(f"📝 Сообщение: {formatted_msg}")
        print("=" * 80)
        
        # Здесь можно добавить отправку в Slack, Discord, email и т.д.
        # await send_to_slack(severity, formatted_msg)
        # await send_to_discord(severity, formatted_msg)
        # await send_email_notification(severity, formatted_msg)
    
    async def monitor_deployment_realtime(self, max_wait_minutes: int = 15):
        """Основной цикл мониторинга"""
        print(f"🔍 Начинаем мониторинг деплоя {self.deploy_id}")
        print(f"📊 Сервис: {self.service_id}")
        print(f"⏰ Максимальное время: {max_wait_minutes} минут")
        print("=" * 80)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=max_wait_minutes)
        
        issues_summary = {
            "critical": [],
            "build_warnings": [],
            "app_warnings": [],
            "errors": [],
            "warnings": []
        }
        
        while datetime.now() < end_time:
            try:
                # Проверяем статус деплоя
                status = await self.get_deploy_status()
                if status:
                    print(f"📈 Статус деплоя: {status}")
                    
                    if status in ["live", "update_failed", "build_failed"]:
                        print(f"🏁 Деплой завершен со статусом: {status}")
                        break
                
                # Получаем и анализируем логи сборки
                build_logs = await self.get_build_logs()
                for log in build_logs:
                    log_id = f"{log.get('timestamp', '')}_{hash(log.get('message', ''))}"
                    if log_id not in self.processed_log_ids:
                        self.processed_log_ids.add(log_id)
                        
                        severity = self.analyze_log_severity(log)
                        formatted_msg = self.format_log_message(log)
                        
                        # Сохраняем в сводку
                        if severity == "critical":
                            issues_summary["critical"].append(log)
                        elif severity == "build_warning":
                            issues_summary["build_warnings"].append(log)
                        elif severity == "error":
                            issues_summary["errors"].append(log)
                        elif severity == "warning":
                            issues_summary["warnings"].append(log)
                        
                        # Выводим лог
                        if severity == "critical":
                            print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА: {formatted_msg}")
                        elif severity == "build_warning":
                            print(f"🔨 ПРЕДУПРЕЖДЕНИЕ СБОРКИ: {formatted_msg}")
                        elif severity == "error":
                            print(f"❌ ОШИБКА: {formatted_msg}")
                        elif severity == "warning":
                            print(f"⚠️  ПРЕДУПРЕЖДЕНИЕ: {formatted_msg}")
                        elif "successful" in log.get("message", "").lower():
                            print(f"✅ УСПЕХ: {formatted_msg}")
                        else:
                            print(f"ℹ️  ИНФО: {formatted_msg}")
                        
                        # Отправляем уведомление если нужно
                        if self.should_notify(severity, log):
                            await self.send_notification(severity, log)
                
                # Получаем и анализируем логи приложения
                app_logs = await self.get_app_logs()
                for log in app_logs:
                    log_id = f"{log.get('timestamp', '')}_{hash(log.get('message', ''))}"
                    if log_id not in self.processed_log_ids:
                        self.processed_log_ids.add(log_id)
                        
                        severity = self.analyze_log_severity(log)
                        formatted_msg = self.format_log_message(log)
                        
                        # Сохраняем в сводку
                        if severity == "critical":
                            issues_summary["critical"].append(log)
                        elif severity == "app_warning":
                            issues_summary["app_warnings"].append(log)
                        elif severity == "error":
                            issues_summary["errors"].append(log)
                        elif severity == "warning":
                            issues_summary["warnings"].append(log)
                        
                        # Выводим лог
                        if severity == "critical":
                            print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА: {formatted_msg}")
                        elif severity == "app_warning":
                            print(f"🐛 ПРЕДУПРЕЖДЕНИЕ ПРИЛОЖЕНИЯ: {formatted_msg}")
                        elif severity == "error":
                            print(f"❌ ОШИБКА: {formatted_msg}")
                        elif severity == "warning":
                            print(f"⚠️  ПРЕДУПРЕЖДЕНИЕ: {formatted_msg}")
                        else:
                            print(f"ℹ️  ИНФО: {formatted_msg}")
                        
                        # Отправляем уведомление если нужно
                        if self.should_notify(severity, log):
                            await self.send_notification(severity, log)
                
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
        total_issues = sum(len(issues) for issues in issues_summary.values())
        
        print("\n" + "=" * 80)
        print("📊 ФИНАЛЬНАЯ СВОДКА МОНИТОРИНГА")
        print("=" * 80)
        print(f"⏱️  Длительность: {duration}")
        print(f"🚨 Критические ошибки: {len(issues_summary['critical'])}")
        print(f"🔨 Предупреждения сборки: {len(issues_summary['build_warnings'])}")
        print(f"🐛 Предупреждения приложения: {len(issues_summary['app_warnings'])}")
        print(f"❌ Обычные ошибки: {len(issues_summary['errors'])}")
        print(f"⚠️  Предупреждения: {len(issues_summary['warnings'])}")
        print(f"📈 Всего проблем: {total_issues}")
        
        # Детальная информация о критических ошибках
        if issues_summary["critical"]:
            print("\n🚨 КРИТИЧЕСКИЕ ОШИБКИ:")
            for issue in issues_summary["critical"]:
                print(f"  - {self.format_log_message(issue)}")
        
        return {
            "issues_summary": issues_summary,
            "total_issues": total_issues,
            "duration": str(duration),
            "deploy_status": await self.get_deploy_status()
        }

async def main():
    """Главная функция"""
    if len(sys.argv) < 3:
        print("Использование: python real_render_monitor.py <service_id> <deploy_id> [max_wait_minutes]")
        print("Пример: python real_render_monitor.py srv-d3bv87r7mgec73a336s0 dep-d3g3ld49c44c73a8cgk0 15")
        sys.exit(1)
    
    service_id = sys.argv[1]
    deploy_id = sys.argv[2]
    max_wait = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    
    monitor = RealRenderMonitor(service_id, deploy_id)
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
