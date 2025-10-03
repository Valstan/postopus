#!/usr/bin/env python3
"""
Быстрый запуск мониторинга логов Render
"""
import subprocess
import sys
import os

def run_monitor(service_id: str, deploy_id: str, max_wait: int = 15):
    """Запускает мониторинг логов"""
    print(f"🚀 Запускаем мониторинг деплоя {deploy_id}")
    print(f"📊 Сервис: {service_id}")
    print(f"⏰ Максимальное время ожидания: {max_wait} минут")
    print("-" * 60)
    
    try:
        # Запускаем мониторинг
        result = subprocess.run([
            sys.executable, 
            "render_log_monitor.py", 
            service_id, 
            deploy_id, 
            str(max_wait)
        ], check=True)
        
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка мониторинга: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Мониторинг прерван пользователем")
        return False

def main():
    """Главная функция"""
    if len(sys.argv) < 3:
        print("Использование: python quick_monitor.py <service_id> <deploy_id> [max_wait_minutes]")
        print("\nПримеры:")
        print("  python quick_monitor.py srv-d3bv87r7mgec73a336s0 dep-d3g3ld49c44c73a8cgk0")
        print("  python quick_monitor.py srv-d3bv87r7mgec73a336s0 dep-d3g3ld49c44c73a8cgk0 20")
        sys.exit(1)
    
    service_id = sys.argv[1]
    deploy_id = sys.argv[2]
    max_wait = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    
    success = run_monitor(service_id, deploy_id, max_wait)
    
    if success:
        print("\n✅ Мониторинг завершен успешно")
        sys.exit(0)
    else:
        print("\n❌ Мониторинг завершен с ошибками")
        sys.exit(1)

if __name__ == "__main__":
    main()
