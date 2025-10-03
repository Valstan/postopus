#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция мониторинга логов с существующими деплоями Postopus
"""
import asyncio
import json
from datetime import datetime
import sys
import os

# ID сервисов Postopus на Render
POSTOPUS_SERVICES = {
    "web": "srv-d3bv87r7mgec73a336s0",  # postopus-web-only
    "worker": "srv-d3bv87r7mgec73a336s1",  # postopus-worker  
    "scheduler": "srv-d3bv87r7mgec73a336s2",  # postopus-scheduler
    "redis": "srv-d3bv87r7mgec73a336s3",  # postopus-redis
    "postgres": "srv-d3bv87r7mgec73a336s4"  # postopus-postgres
}

class PostopusDeploymentMonitor:
    """Монитор деплоя для всех сервисов Postopus"""
    
    def __init__(self):
        self.services = POSTOPUS_SERVICES
        self.monitoring_tasks = []
        
    async def monitor_service_deployment(self, service_name: str, service_id: str, deploy_id: str):
        """Мониторит деплой конкретного сервиса"""
        print(f"🔍 Начинаем мониторинг {service_name} (ID: {service_id})")
        
        try:
            # Здесь будет реальный вызов мониторинга
            # Пока симулируем
            await asyncio.sleep(2)
            print(f"✅ Мониторинг {service_name} завершен")
            
        except Exception as e:
            print(f"❌ Ошибка мониторинга {service_name}: {e}")
    
    async def monitor_all_services(self, deploy_ids: dict = None):
        """Мониторит деплой всех сервисов"""
        print("🚀 Начинаем мониторинг всех сервисов Postopus")
        print("=" * 80)
        
        if not deploy_ids:
            # Если не указаны ID деплоев, используем последние
            deploy_ids = {
                "web": "dep-latest-web",
                "worker": "dep-latest-worker", 
                "scheduler": "dep-latest-scheduler"
            }
        
        # Создаем задачи мониторинга для каждого сервиса
        tasks = []
        for service_name, service_id in self.services.items():
            if service_name in deploy_ids:
                deploy_id = deploy_ids[service_name]
                task = asyncio.create_task(
                    self.monitor_service_deployment(service_name, service_id, deploy_id)
                )
                tasks.append(task)
        
        # Ждем завершения всех задач
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        print("\n✅ Мониторинг всех сервисов завершен")
    
    def get_service_info(self, service_name: str) -> dict:
        """Возвращает информацию о сервисе"""
        if service_name not in self.services:
            return {"error": f"Сервис {service_name} не найден"}
        
        return {
            "name": service_name,
            "id": self.services[service_name],
            "url": f"https://{service_name}.onrender.com" if service_name != "redis" and service_name != "postgres" else None
        }
    
    def list_services(self):
        """Выводит список всех сервисов"""
        print("Сервисы Postopus на Render:")
        print("-" * 50)
        for name, service_id in self.services.items():
            info = self.get_service_info(name)
            print(f"{name.upper()}: {service_id}")
            if info.get("url"):
                print(f"   URL: {info['url']}")
        print("-" * 50)

async def main():
    """Главная функция"""
    monitor = PostopusDeploymentMonitor()
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python postopus_monitor.py list                    # Показать все сервисы")
        print("  python postopus_monitor.py monitor <service>       # Мониторить конкретный сервис")
        print("  python postopus_monitor.py monitor-all             # Мониторить все сервисы")
        print("\nДоступные сервисы:", ", ".join(POSTOPUS_SERVICES.keys()))
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        monitor.list_services()
        
    elif command == "monitor":
        if len(sys.argv) < 3:
            print("Укажите сервис для мониторинга")
            print("Доступные сервисы:", ", ".join(POSTOPUS_SERVICES.keys()))
            sys.exit(1)
        
        service_name = sys.argv[2]
        if service_name not in POSTOPUS_SERVICES:
            print(f"Сервис {service_name} не найден")
            print("Доступные сервисы:", ", ".join(POSTOPUS_SERVICES.keys()))
            sys.exit(1)
        
        service_id = POSTOPUS_SERVICES[service_name]
        deploy_id = sys.argv[3] if len(sys.argv) > 3 else "dep-latest"
        
        await monitor.monitor_service_deployment(service_name, service_id, deploy_id)
        
    elif command == "monitor-all":
        deploy_ids = {}
        if len(sys.argv) > 2:
            # Парсим дополнительные аргументы для ID деплоев
            for arg in sys.argv[2:]:
                if "=" in arg:
                    service, deploy_id = arg.split("=", 1)
                    deploy_ids[service] = deploy_id
        
        await monitor.monitor_all_services(deploy_ids)
        
    else:
        print(f"Неизвестная команда: {command}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
