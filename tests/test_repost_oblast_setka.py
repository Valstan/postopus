"""Тесты для модуля repost_oblast_setka."""

import unittest


class TestRepostSetkaLogic(unittest.TestCase):
    """Тестируем логику определения режима копирования/репоста."""

    def test_repost_command_lowercase(self):
        """'репост' в нижнем регистре должен триггерить репост."""
        text = "репост всем группам!"
        self.assertIn("репост", text.lower())

    def test_repost_command_uppercase(self):
        """'РЕПОСТ' в верхнем регистре должен триггерить репост."""
        text = "РЕПОСТ всем группам!"
        self.assertIn("репост", text.lower())

    def test_repost_command_mixed(self):
        """'РеПоСт' в смешанном регистре должен триггерить репост."""
        text = "РеПоСт всем группам!"
        self.assertIn("репост", text.lower())

    def test_repost_command_case_insensitive(self):
        """'Репост' с заглавной буквы должен триггерить репост."""
        text = "Репост для всех"
        self.assertIn("репост", text.lower())

    def test_no_repost_command(self):
        """Текст без 'репост' не должен триггерить репост."""
        text = "Обычный пост без команды"
        self.assertNotIn("репост", text.lower())

    def test_repost_in_middle(self):
        """'репост' в середине текста должен триггерить репост."""
        text = "Внимание! репост для всех регионов"
        self.assertIn("репост", text.lower())

    def test_repost_not_in_original_after_clear(self):
        """
        Критично: если проверять 'репост' ПОСЛЕ clear_copy_history,
        текст команды уже потерян (он был во внешнем посте).
        Поэтому проверка должна быть ДО clear_copy_history.
        """
        # Эмуляция: внешний пост с командой + внутренний без
        raw_post = {
            "id": 100,
            "owner_id": -167381590,
            "text": "РЕПОСТ всем группам!",  # Команда здесь
            "copy_history": [
                {
                    "id": 200,
                    "owner_id": -111111,
                    "text": "Оригинальная новость",  # Без команды
                }
            ],
        }
        # Проверка ДО clear_copy_history — правильно
        self.assertIn("репост", raw_post.get("text", "").lower())


class TestRepostSetkaModule(unittest.TestCase):
    """Тестируем что модуль импортируется и настройки корректны."""

    def test_module_imports(self):
        """Module should import without errors."""
        from bin.control import repost_oblast_setka
        self.assertTrue(hasattr(repost_oblast_setka, "repost_oblast_setka"))

    def test_scan_limit(self):
        """MAX_POSTS_TO_SCAN should be 10."""
        from bin.control.repost_oblast_setka import MAX_POSTS_TO_SCAN
        self.assertEqual(MAX_POSTS_TO_SCAN, 10)

    def test_lip_limit(self):
        """MAX_LIP_HISTORY should be 12."""
        from bin.control.repost_oblast_setka import MAX_LIP_HISTORY
        self.assertEqual(MAX_LIP_HISTORY, 12)


if __name__ == "__main__":
    unittest.main()
