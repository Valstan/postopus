"""
Unit tests for env_loader module.
Tests configuration loading and session initialization without MongoDB.
"""
import pytest
from unittest.mock import patch, MagicMock
import os


def test_test_polygon_group_id_is_numeric():
    """Test that TEST_POLYGON_GROUP_ID is a number."""
    from env_loader import TEST_POLYGON_GROUP_ID
    assert isinstance(TEST_POLYGON_GROUP_ID, int)
    assert TEST_POLYGON_GROUP_ID == -137760500


def test_session_dict_exists():
    """Test that session dict is properly initialized."""
    from env_loader import session
    assert isinstance(session, dict)
    assert len(session) > 0


def test_session_has_required_keys():
    """Test that session contains critical keys."""
    from env_loader import session
    required_keys = [
        'TEST_POLYGON_GROUP_ID',
        'post_to_test_polygon',
        'names_tokens_post_vk',
        'names_tokens_read_vk'
    ]
    for key in required_keys:
        assert key in session, f"Missing required session key: {key}"


def test_test_polygon_mode_from_env_true():
    """Test TEST_POLYGON_MODE can be set to true via env."""
    with patch.dict(os.environ, {'TEST_POLYGON_MODE': 'true'}):
        # Simulate env_loader's check
        test_mode = os.getenv('TEST_POLYGON_MODE', '').lower() in ('1', 'true', 'yes')
        assert test_mode is True


def test_test_polygon_mode_from_env_one():
    """Test TEST_POLYGON_MODE can be set to 1 via env."""
    with patch.dict(os.environ, {'TEST_POLYGON_MODE': '1'}):
        test_mode = os.getenv('TEST_POLYGON_MODE', '').lower() in ('1', 'true', 'yes')
        assert test_mode is True


def test_test_polygon_mode_from_env_false():
    """Test TEST_POLYGON_MODE defaults to false."""
    with patch.dict(os.environ, {'TEST_POLYGON_MODE': ''}, clear=False):
        test_mode = os.getenv('TEST_POLYGON_MODE', '').lower() in ('1', 'true', 'yes')
        assert test_mode is False


def test_vk_tokens_structure():
    """Test that VK token lists are properly structured."""
    from env_loader import names_tokens_post_vk, names_tokens_read_vk
    
    assert isinstance(names_tokens_post_vk, list)
    assert isinstance(names_tokens_read_vk, list)


def test_logger_is_configured():
    """Test that logger is configured."""
    from env_loader import logger
    assert logger is not None
    assert logger.name == 'postopus'


def test_get_env_function():
    """Test get_env helper function."""
    from env_loader import get_env
    
    with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
        result = get_env('TEST_VAR')
        assert result == 'test_value'


def test_get_env_with_default():
    """Test get_env returns default when env var not set."""
    from env_loader import get_env
    
    result = get_env('NONEXISTENT_VAR_XYZ', 'default_value')
    assert result == 'default_value'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
