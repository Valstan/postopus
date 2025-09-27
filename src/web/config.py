"""
Веб-конфигурация приложения PostOpus.
Импортирует общую конфигурацию из src.config.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Экспортируем Config для использования в веб-модуле
__all__ = ['Config']
