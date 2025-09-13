"""
Тесты для PostProcessor.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.models.post import Post, Attachment
from src.models.config import AppConfig, FilterConfig
from src.services.post_processor import PostProcessor


class TestPostProcessor:
    """Тесты для PostProcessor."""
    
    @pytest.fixture
    def config(self):
        """Создает тестовую конфигурацию."""
        config = AppConfig.from_env()
        config.filters = FilterConfig()
        config.filters.time_old_post = {
            'hard': 3600,    # 1 час
            'medium': 7200,  # 2 часа
            'light': 14400   # 4 часа
        }
        config.filters.delete_msg_blacklist = ['spam', 'test']
        config.work = {
            'novost': {
                'lip': [],
                'hash': []
            }
        }
        return config
    
    @pytest.fixture
    def processor(self, config):
        """Создает PostProcessor с тестовой конфигурацией."""
        return PostProcessor(config)
    
    @pytest.fixture
    def sample_post_data(self):
        """Создает тестовые данные поста."""
        return {
            'id': 123,
            'owner_id': -456,
            'from_id': -456,
            'text': 'Test post text',
            'date': int((datetime.now() - timedelta(minutes=30)).timestamp()),
            'views': {'count': 100},
            'attachments': [
                {
                    'type': 'photo',
                    'photo': {
                        'owner_id': -456,
                        'id': 789,
                        'sizes': [
                            {'width': 100, 'height': 100, 'url': 'http://example.com/photo.jpg'}
                        ]
                    }
                }
            ]
        }
    
    def test_create_post_from_data(self, processor, sample_post_data):
        """Тест создания Post из данных."""
        post = processor._create_post_from_data(sample_post_data)
        
        assert post.id == 123
        assert post.owner_id == -456
        assert post.text == 'Test post text'
        assert post.views['count'] == 100
        assert len(post.attachments) == 1
        assert post.attachments[0].type == 'photo'
    
    def test_should_process_post_fresh(self, processor, sample_post_data):
        """Тест обработки свежего поста."""
        post = processor._create_post_from_data(sample_post_data)
        result = processor._should_process_post(post, 'novost')
        
        assert result is True
    
    def test_should_process_post_old(self, processor):
        """Тест обработки старого поста."""
        old_data = {
            'id': 123,
            'owner_id': -456,
            'from_id': -456,
            'text': 'Old post',
            'date': int((datetime.now() - timedelta(hours=2)).timestamp()),
            'views': {'count': 100}
        }
        
        post = processor._create_post_from_data(old_data)
        result = processor._should_process_post(post, 'novost')
        
        assert result is False
    
    def test_should_process_post_blacklisted_text(self, processor, sample_post_data):
        """Тест обработки поста с запрещенными словами."""
        sample_post_data['text'] = 'This is spam content'
        post = processor._create_post_from_data(sample_post_data)
        result = processor._should_process_post(post, 'novost')
        
        assert result is False
    
    def test_should_process_post_blacklisted_source(self, processor, sample_post_data):
        """Тест обработки поста из запрещенного источника."""
        processor.config.filters.black_id = [456]
        sample_post_data['owner_id'] = 456
        
        post = processor._create_post_from_data(sample_post_data)
        result = processor._should_process_post(post, 'novost')
        
        assert result is False
    
    def test_is_duplicate(self, processor, sample_post_data):
        """Тест проверки дубликатов."""
        post = processor._create_post_from_data(sample_post_data)
        post_id = post.get_unique_id()
        
        # Добавляем пост в список обработанных
        processor.config.work['novost']['lip'].append(post_id)
        
        result = processor._is_duplicate(post, 'novost')
        assert result is True
    
    def test_check_theme_specific_rules_sosed(self, processor, sample_post_data):
        """Тест правил для темы 'sosed'."""
        post = processor._create_post_from_data(sample_post_data)
        
        # Пост без хештега #Новости
        result = processor._check_theme_specific_rules(post, 'sosed')
        assert result is False
        
        # Пост с хештегом #Новости
        post.text = 'News post #Новости'
        result = processor._check_theme_specific_rules(post, 'sosed')
        assert result is True
    
    def test_check_theme_specific_rules_kino(self, processor, sample_post_data):
        """Тест правил для темы 'kino'."""
        post = processor._create_post_from_data(sample_post_data)
        
        # Пост без видео
        result = processor._check_theme_specific_rules(post, 'kino')
        assert result is False
        
        # Пост с видео
        post.attachments = [Attachment(type='video', owner_id=-456, id=789)]
        result = processor._check_theme_specific_rules(post, 'kino')
        assert result is True
    
    def test_check_theme_specific_rules_prikol(self, processor, sample_post_data):
        """Тест правил для темы 'prikol'."""
        post = processor._create_post_from_data(sample_post_data)
        
        # Короткий пост
        post.text = 'Short'
        result = processor._check_theme_specific_rules(post, 'prikol')
        assert result is True
        
        # Длинный пост
        post.text = 'A' * 150
        result = processor._check_theme_specific_rules(post, 'prikol')
        assert result is False
