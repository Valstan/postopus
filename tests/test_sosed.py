"""
Тесты для контроллера sosed
"""
import unittest
from unittest.mock import patch, MagicMock
from bin.control.sosed import sosed


class TestSosed(unittest.TestCase):
    """Тесты для функции sosed()"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.mock_session = {
            "sosed": "neighbor1,neighbor2,neighbor3",
            "work": {
                "sosed": {
                    "lip": []
                }
            },
            "all_my_groups": {
                "neighbor1_group": -123456,
                "neighbor2_group": -789012,
                "main_group": -999999
            }
        }

    @patch('bin.control.sosed.session', new_callable=MagicMock)
    @patch('bin.control.sosed.get_msg')
    @patch('bin.control.sosed.posting_post')
    @patch('bin.control.sosed.search_text')
    @patch('bin.control.sosed.send_error')
    def test_sosed_no_posts_from_neighbor(
        self, mock_send_error, mock_search, mock_posting, mock_get_msg, mock_session
    ):
        """Тест: sosed с пустым списком постов от соседа"""
        # Arrange
        mock_search.return_value = True  # Нашли соседа
        mock_get_msg.return_value = []  # Но постов нет
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        mock_session.__getitem__.return_value = self.mock_session["sosed"]
        
        # Act
        sosed()
        
        # Assert - posting_post не должен быть вызван
        mock_posting.assert_not_called()
        mock_send_error.assert_not_called()

    @patch('bin.control.sosed.session', new_callable=MagicMock)
    @patch('bin.control.sosed.get_msg')
    @patch('bin.control.sosed.posting_post')
    @patch('bin.control.sosed.lip_of_post')
    @patch('bin.control.sosed.search_text')
    @patch('bin.control.sosed.send_error')
    def test_sosed_all_posts_already_published(
        self, mock_send_error, mock_search, mock_lip, mock_posting, mock_get_msg, mock_session
    ):
        """Тест: sosed с уже опубликованными постами (без #Новости)"""
        # Arrange
        mock_post_data = {
            "id": 1, 
            "text": "Test post without news tag", 
            "owner_id": -123456,
            "views": {"count": 100}
        }
        
        # search_text возвращает True для поиска имени соседа в имени группы
        # Но для "#Новости" в тексте возвращаем False (хэштега нет)
        def search_text_side_effect(patterns, text):
            if "#Новости" in patterns:
                return False  # Хэштега #Новости в тексте нет
            return True  # Имя соседа в имени группы найдено
            
        mock_search.side_effect = search_text_side_effect
        mock_get_msg.return_value = [mock_post_data]
        mock_lip.return_value = "lip_1"
        
        # Все посты уже в lip (опубликованы)
        self.mock_session["work"]["sosed"]["lip"] = ["lip_1"]
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        mock_session.__getitem__.return_value = self.mock_session["sosed"]
        
        # Act
        sosed()
        
        # Assert - posting_post не должен быть вызван
        mock_posting.assert_not_called()
        mock_send_error.assert_not_called()

    @patch('bin.control.sosed.session', new_callable=MagicMock)
    @patch('bin.control.sosed.get_msg')
    @patch('bin.control.sosed.posting_post')
    @patch('bin.control.sosed.lip_of_post')
    @patch('bin.control.sosed.search_text')
    @patch('bin.control.sosed.send_error')
    def test_sosed_successful_posting(
        self, mock_send_error, mock_search, mock_lip, mock_posting, mock_get_msg, mock_session
    ):
        """Тест: sosed успешно публикует посты"""
        # Arrange
        mock_post_data = {
            "id": 1, 
            "text": "#Новости Test post", 
            "owner_id": -123456,
            "views": {"count": 100}
        }
        mock_search.return_value = True
        mock_get_msg.return_value = [mock_post_data]
        mock_lip.return_value = "lip_1"
        
        # Пост еще не опубликован
        self.mock_session["work"]["sosed"]["lip"] = []
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        
        # Act
        sosed()
        
        # Assert - posting_post должен быть вызван
        mock_posting.assert_called_once()
        mock_send_error.assert_not_called()

    @patch('bin.control.sosed.session', new_callable=MagicMock)
    @patch('bin.control.sosed.random.choice')
    @patch('bin.control.sosed.get_msg')
    @patch('bin.control.sosed.posting_post')
    @patch('bin.control.sosed.send_error')
    def test_sosed_handles_vk_api_error(
        self, mock_send_error, mock_posting, mock_get_msg, mock_choice, mock_session
    ):
        """Тест: sosed обрабатывает ошибки VK API"""
        # Arrange
        mock_choice.return_value = "neighbor1"
        mock_session.__getitem__.side_effect = self.mock_session.__getitem__
        mock_get_msg.side_effect = Exception("VK API error")
        
        # Act
        sosed()
        
        # Assert - send_error должен быть вызван
        mock_send_error.assert_called_once()


if __name__ == '__main__':
    unittest.main()
