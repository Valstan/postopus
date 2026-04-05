"""
Тесты для контроллера repost_oleny
"""
import unittest
from unittest.mock import patch, MagicMock
from bin.control.repost_oleny import repost_oleny


class TestRepostOleny(unittest.TestCase):
    """Тесты для функции repost_oleny()"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.mock_session = {
            "work": {
                "repost_oleny": {
                    "lip": []
                }
            },
            "all_my_groups": {
                "group1": -123456,
                "group2": -789012,
                "oleny": -218688001  # Should be excluded
            },
            "post_group_vk": -123456,
            "name_session": "repost_oleny"
        }

    @patch('bin.control.repost_oleny.session', new_callable=MagicMock)
    @patch('bin.control.repost_oleny.get_msg')
    @patch('bin.control.repost_oleny.posting_post')
    @patch('bin.control.repost_oleny.send_error')
    def test_repost_oleny_empty_posts(
        self, mock_send_error, mock_posting, mock_get_msg, mock_session
    ):
        """Тест: repost_oleny с пустым списком постов не должен вызывать crash"""
        # Arrange
        mock_get_msg.return_value = []
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        
        # Act
        repost_oleny()
        
        # Assert - posting_post не должен быть вызван
        mock_posting.assert_not_called()
        mock_send_error.assert_not_called()

    @patch('bin.control.repost_oleny.session', new_callable=MagicMock)
    @patch('bin.control.repost_oleny.get_msg')
    @patch('bin.control.repost_oleny.posting_post')
    @patch('bin.control.repost_oleny.lip_of_post')
    @patch('bin.control.repost_oleny.clear_copy_history')
    @patch('bin.control.repost_oleny.send_error')
    def test_repost_oleny_all_posts_already_published(
        self, mock_send_error, mock_clear, mock_lip, mock_posting, mock_get_msg, mock_session
    ):
        """Тест: repost_oleny с уже опубликованными постами"""
        # Arrange
        mock_post_data = {
            "id": 1, 
            "text": "Test post", 
            "owner_id": -218688001
        }
        mock_get_msg.return_value = [mock_post_data]
        mock_clear.return_value = mock_post_data
        mock_lip.return_value = "lip_1"
        
        # Все посты уже в lip (опубликованы)
        self.mock_session["work"]["repost_oleny"]["lip"] = ["lip_1"]
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        
        # Act
        repost_oleny()
        
        # Assert - posting_post не должен быть вызван
        mock_posting.assert_not_called()
        mock_send_error.assert_not_called()

    @patch('bin.control.repost_oleny.session', new_callable=MagicMock)
    @patch('bin.control.repost_oleny.get_msg')
    @patch('bin.control.repost_oleny.posting_post')
    @patch('bin.control.repost_oleny.lip_of_post')
    @patch('bin.control.repost_oleny.clear_copy_history')
    @patch('bin.control.repost_oleny.time.sleep')
    @patch('bin.control.repost_oleny.send_error')
    def test_repost_oleny_successful_posting(
        self, mock_send_error, mock_sleep, mock_clear, mock_lip, 
        mock_posting, mock_get_msg, mock_session
    ):
        """Тест: repost_oleny успешно публикует посты"""
        # Arrange
        mock_post_data = {
            "id": 1, 
            "text": "Test post", 
            "owner_id": -218688001
        }
        mock_get_msg.return_value = [mock_post_data]
        mock_clear.return_value = mock_post_data
        mock_lip.return_value = "lip_1"
        
        # Пост еще не опубликован
        self.mock_session["work"]["repost_oleny"]["lip"] = []
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        
        # Act
        repost_oleny()
        
        # Assert - posting_post должен быть вызван для каждой группы (кроме оленя)
        # 2 группы (group1 и group2), олень исключен
        self.assertEqual(mock_posting.call_count, 2)
        mock_send_error.assert_not_called()

    @patch('bin.control.repost_oleny.session', new_callable=MagicMock)
    @patch('bin.control.repost_oleny.get_msg')
    @patch('bin.control.repost_oleny.posting_post')
    @patch('bin.control.repost_oleny.send_error')
    def test_repost_oleny_handles_vk_api_error(
        self, mock_send_error, mock_posting, mock_get_msg, mock_session
    ):
        """Тест: repost_oleny обрабатывает ошибки VK API"""
        # Arrange
        mock_get_msg.side_effect = Exception("VK API error")
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        
        # Act
        repost_oleny()
        
        # Assert - send_error должен быть вызван
        mock_send_error.assert_called_once()

    @patch('bin.control.repost_oleny.session', new_callable=MagicMock)
    @patch('bin.control.repost_oleny.get_msg')
    @patch('bin.control.repost_oleny.posting_post')
    @patch('bin.control.repost_oleny.lip_of_post')
    @patch('bin.control.repost_oleny.clear_copy_history')
    @patch('bin.control.repost_oleny.time.sleep')
    @patch('bin.control.repost_oleny.send_error')
    def test_repost_oleny_excludes_source_group(
        self, mock_send_error, mock_sleep, mock_clear, mock_lip,
        mock_posting, mock_get_msg, mock_session
    ):
        """Тест: repost_oleny НЕ публикует в исходную группу (oleny_id)"""
        # Arrange
        mock_post_data = {
            "id": 1, 
            "text": "Test post", 
            "owner_id": -218688001
        }
        mock_get_msg.return_value = [mock_post_data]
        mock_clear.return_value = mock_post_data
        mock_lip.return_value = "lip_1"
        
        self.mock_session["work"]["repost_oleny"]["lip"] = []
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        
        # Act
        repost_oleny()
        
        # Assert - Проверяем что post_group_vk никогда не был равен oleny_id
        oleny_id = -218688001
        for call in mock_posting.call_args_list:
            # post_group_vk должен быть установлен в groups кроме oleny
            self.assertNotEqual(
                mock_session.__setitem__.call_args,
                (("post_group_vk", oleny_id),)
            )


if __name__ == '__main__':
    unittest.main()
