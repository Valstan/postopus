#!/usr/bin/env python3
"""
Автоматический мониторинг логов Render во время деплоя
с уведомлениями о критических ошибках и фильтрацией
"""
import time
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio

class LogLevel:
    """Уровни важности логов"""
    CRITICAL = "critical"
    ERROR = "error" 
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"

class DeploymentMonitor:
    """Монитор деплоя с автоматическими уведомлениями"""
    
    def __init__(self, service_id: str, deploy_id: str):
        self.service_id = service_id
        self.deploy_id = deploy_id
        self.start_time = datetime.now()
        self.critical_errors = []
        self.build_errors = []
        self.app_errors = []
        
    def log_message(self, level: str, message: str, category: str = "general"):
        """Логирует сообщение с временной меткой"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level.upper()}: {message}")
        
        # Сохраняем критические ошибки
        if level in [LogLevel.CRITICAL, LogLevel.ERROR]:
            error_info = {
                "timestamp": timestamp,
                "level": level,
                "message": message,
                "category": category
            }
            
            if category == "build":
                self.build_errors.append(error_info)
            elif category == "app":
                self.app_errors.append(error_info)
            else:
                self.critical_errors.append(error_info)
    
    def check_deploy_status(self) -> Optional[str]:
        """Проверяет статус деплоя через MCP Render API"""
        try:
            # Здесь будет реальный вызов MCP API
            # Пока симулируем проверку
            return "build_in_progress"  # или "live", "update_failed", etc.
        except Exception as e:
            self.log_message(LogLevel.ERROR, f"Ошибка проверки статуса деплоя: {e}")
            return None
    
    def analyze_logs(self, logs: List[Dict]) -> Dict[str, List]:
        """Анализирует логи и фильтрует по важности"""
        filtered_logs = {
            "critical": [],
            "errors": [],
            "warnings": [],
            "info": [],
            "build_issues": [],
            "app_issues": []
        }
        
        for log in logs:
            level = log.get("level", "info").lower()
            message = log.get("message", "")
            log_type = log.get("type", "app")
            
            # Фильтрация критических ошибок
            if any(keyword in message.lower() for keyword in [
                "traceback", "exception", "fatal", "critical", 
                "indentationerror", "syntaxerror", "importerror"
            ]):
                filtered_logs["critical"].append(log)
                self.log_message(LogLevel.CRITICAL, f"КРИТИЧЕСКАЯ ОШИБКА: {message}", log_type)
            
            # Фильтрация ошибок сборки
            elif log_type == "build" and level == "error":
                filtered_logs["build_issues"].append(log)
                self.log_message(LogLevel.ERROR, f"Ошибка сборки: {message}", "build")
            
            # Фильтрация ошибок приложения
            elif log_type == "app" and level == "error":
                filtered_logs["app_issues"].append(log)
                self.log_message(LogLevel.ERROR, f"Ошибка приложения: {message}", "app")
            
            # Обычные ошибки
            elif level == "error":
                filtered_logs["errors"].append(log)
                self.log_message(LogLevel.ERROR, message)
            
            # Предупреждения
            elif level == "warning":
                filtered_logs["warnings"].append(log)
                self.log_message(LogLevel.WARNING, message)
            
            # Информационные сообщения
            elif level == "info":
                filtered_logs["info"].append(log)
                if "successful" in message.lower() or "build successful" in message.lower():
                    self.log_message(LogLevel.INFO, f"✅ {message}")
        
        return filtered_logs
    
    def send_notification(self, level: str, message: str, details: Dict = None):
        """Отправляет уведомление о критической ошибке"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        notification = {
            "timestamp": timestamp,
            "level": level,
            "service_id": self.service_id,
            "deploy_id": self.deploy_id,
            "message": message,
            "details": details or {}
        }
        
        # Здесь можно добавить отправку в Slack, Discord, email и т.д.
        print(f"\n🚨 УВЕДОМЛЕНИЕ [{level.upper()}] 🚨")
        print(f"Сервис: {self.service_id}")
        print(f"Деплой: {self.deploy_id}")
        print(f"Сообщение: {message}")
        if details:
            print(f"Детали: {json.dumps(details, indent=2, ensure_ascii=False)}")
        print("=" * 60)
    
    def get_logs_summary(self) -> Dict:
        """Возвращает сводку по логам"""
        return {
            "deploy_id": self.deploy_id,
            "service_id": self.service_id,
            "duration": str(datetime.now() - self.start_time),
            "critical_errors": len(self.critical_errors),
            "build_errors": len(self.build_errors),
            "app_errors": len(self.app_errors),
            "total_issues": len(self.critical_errors) + len(self.build_errors) + len(self.app_errors)
        }
    
    async def monitor_deployment(self, max_wait_minutes: int = 15):
        """Основной цикл мониторинга деплоя"""
        self.log_message(LogLevel.INFO, f"Начинаем мониторинг деплоя {self.deploy_id}")
        self.log_message(LogLevel.INFO, f"Максимальное время ожидания: {max_wait_minutes} минут")
        
        end_time = datetime.now() + timedelta(minutes=max_wait_minutes)
        check_interval = 30  # Проверяем каждые 30 секунд
        last_log_count = 0
        
        while datetime.now() < end_time:
            try:
                # Проверяем статус деплоя
                status = self.check_deploy_status()
                if status:
                    self.log_message(LogLevel.INFO, f"Статус деплоя: {status}")
                    
                    # Если деплой завершился
                    if status in ["live", "update_failed", "build_failed"]:
                        self.log_message(LogLevel.INFO, f"Деплой завершен со статусом: {status}")
                        break
                
                # Получаем новые логи (здесь будет реальный MCP вызов)
                # Пока симулируем получение логов
                await asyncio.sleep(check_interval)
                
                # Проверяем критические ошибки
                if self.critical_errors:
                    latest_error = self.critical_errors[-1]
                    self.send_notification(
                        LogLevel.CRITICAL,
                        f"Обнаружена критическая ошибка: {latest_error['message']}",
                        latest_error
                    )
                
                # Проверяем ошибки сборки
                if self.build_errors:
                    latest_build_error = self.build_errors[-1]
                    self.send_notification(
                        LogLevel.ERROR,
                        f"Ошибка сборки: {latest_build_error['message']}",
                        latest_build_error
                    )
                
            except KeyboardInterrupt:
                self.log_message(LogLevel.WARNING, "Мониторинг остановлен пользователем")
                break
            except Exception as e:
                self.log_message(LogLevel.ERROR, f"Ошибка мониторинга: {e}")
                await asyncio.sleep(10)
        
        # Финальная сводка
        summary = self.get_logs_summary()
        self.log_message(LogLevel.INFO, "Мониторинг завершен")
        self.log_message(LogLevel.INFO, f"Сводка: {json.dumps(summary, indent=2, ensure_ascii=False)}")
        
        return summary

async def main():
    """Главная функция"""
    if len(sys.argv) < 3:
        print("Использование: python monitor_logs.py <service_id> <deploy_id> [max_wait_minutes]")
        print("Пример: python monitor_logs.py srv-d3bv87r7mgec73a336s0 dep-d3g3ld49c44c73a8cgk0 15")
        sys.exit(1)
    
    service_id = sys.argv[1]
    deploy_id = sys.argv[2]
    max_wait = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    
    monitor = DeploymentMonitor(service_id, deploy_id)
    summary = await monitor.monitor_deployment(max_wait)
    
    # Возвращаем код выхода в зависимости от результата
    if summary["total_issues"] > 0:
        print(f"\n❌ Деплой завершен с {summary['total_issues']} проблемами")
        sys.exit(1)
    else:
        print(f"\n✅ Деплой завершен успешно")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())