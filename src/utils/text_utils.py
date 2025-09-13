"""
Утилиты для работы с текстом.
"""
import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class TextProcessor:
    """Класс для обработки текста."""
    
    def __init__(self):
        # TODO: Загружать blacklist из базы данных
        self.blacklist = [
            "реклама", "спам", "продам", "куплю", "обменяю",
            "заработок", "деньги", "кредит", "займ"
        ]
    
    def contains_blacklisted_words(self, text: str) -> bool:
        """
        Проверяет, содержит ли текст запрещенные слова.
        
        Args:
            text: Текст для проверки
            
        Returns:
            True если содержит запрещенные слова
        """
        if not text or not self.blacklist:
            return False
        
        try:
            # Создаем регулярное выражение из списка запрещенных слов
            pattern = '|'.join(re.escape(word) for word in self.blacklist)
            return bool(re.search(pattern, text, re.IGNORECASE | re.MULTILINE))
        except Exception as e:
            logger.error(f"Error checking blacklisted words: {e}")
            return False
    
    def search_text(self, search_words: List[str], text: str) -> bool:
        """
        Ищет слова в тексте.
        
        Args:
            search_words: Список слов для поиска
            text: Текст для поиска
            
        Returns:
            True если найдено хотя бы одно слово
        """
        if not text or not search_words:
            return False
        
        try:
            pattern = '|'.join(re.escape(word) for word in search_words)
            return bool(re.search(pattern, text, re.IGNORECASE | re.MULTILINE))
        except Exception as e:
            logger.error(f"Error searching text: {e}")
            return False
    
    def clear_text(self, text: str, blacklist_type: str = 'novost') -> str:
        """
        Очищает текст от нежелательных слов.
        
        Args:
            text: Текст для очистки
            blacklist_type: Тип черного списка (novost, reklama)
            
        Returns:
            Очищенный текст
        """
        if not text:
            return text
        
        try:
            # TODO: Загружать blacklist из базы данных по типу
            blacklist = self.blacklist
            if not blacklist:
                return text
            
            # Удаляем нежелательные слова
            pattern = '|'.join(re.escape(word) for word in blacklist)
            cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
            
            # Убираем лишние пробелы
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            
            # Убираем пробелы в начале и конце
            cleaned_text = cleaned_text.strip()
            
            return cleaned_text
        except Exception as e:
            logger.error(f"Error clearing text: {e}")
            return text
    
    def text_to_rafinad(self, text: str) -> str:
        """
        Преобразует текст в рафинад (упрощенную форму для сравнения).
        
        Args:
            text: Исходный текст
            
        Returns:
            Упрощенный текст
        """
        if not text:
            return text
        
        try:
            # Убираем все кроме букв и цифр
            rafinad = re.sub(r'[^\w\s]', '', text.lower())
            # Убираем лишние пробелы
            rafinad = re.sub(r'\s+', ' ', rafinad).strip()
            return rafinad
        except Exception as e:
            logger.error(f"Error converting text to rafinad: {e}")
            return text
    
    def is_text_suitable_for_theme(self, text: str, theme: str) -> bool:
        """
        Проверяет, подходит ли текст для темы.
        
        Args:
            text: Текст для проверки
            theme: Тема поста
            
        Returns:
            True если текст подходит
        """
        if not text:
            return False
        
        # Проверяем длину текста
        text_length = len(text)
        
        if theme == 'reklama':
            # Для рекламы нужен текст от 30 до 250 символов
            return 30 <= text_length <= 250
        
        return True
