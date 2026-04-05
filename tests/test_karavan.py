"""
Тесты для контроллера karavan
"""
import unittest
from unittest.mock import patch, MagicMock
from bin.control.karavan import karavan


class TestKaravan(unittest.TestCase):
    """Тесты для функции karavan()"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.mock_session = {
            "work": {
                "karavan": {
                    "lip": [],
                    "table_size": 10
                }
            },
            "all_my_groups": {
                    "group1": -123456,
                    "group2": -789012,
                    "гоньба": -218688001  # Should be excluded
                },
            "post_group_vk": -123456,
            "name_session": "karavan"
        }

    @patch('bin.control.karavan.session', new_callable=MagicMock)
    @patch('bin.control.karavan.get_msg')
    @patch('bin.control.karavan.posting_post')
    @patch('bin.control.karavan.send_error')
    def test_karavan_empty_posts(self, mock_send_error, mock_posting, mock_get_msg, mock_session):
        """Тест: karavan с пустым списком постов не должен вызывать crash"""
        # Arrange
        mock_get_msg.return_value = []
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        
        # Act
        karavan()
        
        # Assert - posting_post не должен быть вызван
        mock_posting.assert_not_called()
        # send_error не должен быть вызван (это не ошибка, а нормальная ситуация)
        mock_send_error.assert_not_called()

    @patch('bin.control.karavan.session', new_callable=MagicMock)
    @patch('bin.control.karavan.get_msg')
    @patch('bin.control.karavan.posting_post')
    @patch('bin.control.karavan.lip_of_post')
    @patch('bin.control.karavan.clear_copy_history')
    @patch('bin.control.karavan.send_error')
    def test_karavan_all_posts_already_published(
        self, mock_send_error, mock_clear, mock_lip, mock_posting, mock_get_msg, mock_session
    ):
        """Тест: karavan с уже опубликованными постами не должен вызывать crash"""
        # Arrange
        mock_post_data = {"id": 1, "text": "Test post", "owner_id": -175405594}
        mock_get_msg.return_value = [mock_post_data]
        mock_clear.return_value = mock_post_data
        mock_lip.return_value = "lip_1"
        
        # Все посты уже в lip (опубликованы)
        self.mock_session["work"]["karavan"]["lip"] = ["lip_1"]
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        
        # Act
        karavan()
        
        # Assert - posting_post не должен быть вызван
        mock_posting.assert_not_called()
        mock_send_error.assert_not_called()

    @patch('bin.control.karavan.session', new_callable=MagicMock)
    @patch('bin.control.karavan.get_msg')
    @patch('bin.control.karavan.posting_post')
    @patch('bin.control.karavan.lip_of_post')
    @patch('bin.control.karavan.clear_copy_history')
    @patch('bin.control.karavan.random.choice')
    @patch('bin.control.karavan.time.sleep')
    @patch('bin.control.karavan.send_error')
    def test_karavan_successful_posting(
        self, mock_send_error, mock_sleep, mock_choice, mock_clear, 
        mock_lip, mock_posting, mock_get_msg, mock_session
    ):
        """Тест: karavan успешно публикует посты"""
        # Arrange
        mock_post_data = {"id": 1, "text": "Test post", "owner_id": -175405594}
        mock_get_msg.return_value = [mock_post_data]
        mock_clear.return_value = mock_post_data
        mock_lip.return_value = "lip_1"
        mock_choice.return_value = mock_post_data
        
        # Пост еще не опубликован
        self.mock_session["work"]["karavan"]["lip"] = []
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        
        # Act
        karavan()
        
        # Assert - posting_post должен быть вызван для каждой группы (кроме гоньбы)
        # 2 группы (group1 и group2), гоньба исключена
        self.assertEqual(mock_posting.call_count, 2)
        mock_send_error.assert_not_called()

    @patch('bin.control.karavan.session', new_callable=MagicMock)
    @patch('bin.control.karavan.get_msg')
    @patch('bin.control.karavan.posting_post')
    @patch('bin.control.karavan.send_error')
    def test_karavan_handles_vk_api_error(
        self, mock_send_error, mock_posting, mock_get_msg, mock_session
    ):
        """Тест: karavan обрабатывает ошибки VK API"""
        # Arrange
        mock_get_msg.side_effect = Exception("VK API error")
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        
        # Act
        karavan()
        
        # Assert - send_error должен быть вызван
        mock_send_error.assert_called_once()


if __name__ == '__main__':
    unittest.main()
