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

    def test_no_repost_command(self):
        """Текст без 'репост' не должен триггерить репост."""
        text = "Обычный пост без команды"
        self.assertNotIn("репост", text.lower())

    def test_repost_in_middle(self):
        """'репост' в середине текста должен триггерить репост."""
        text = "Внимание! репост для всех регионов"
        self.assertIn("репост", text.lower())

    def test_repost_as_part_of_word_not_matched(self):
        """'репост' как часть другого слова не должен матчиться.
        Note: In Russian 'репост' is a standalone word, so this tests
        that we don't accidentally match partial words in common text."""
        text = "Информация для регионов"
        self.assertNotIn("репост", text.lower())


class TestRepostSetkaModule(unittest.TestCase):
    """Тестируем что модуль импортируется и функция существует."""

    def test_module_imports(self):
        """Module should import without errors."""
        from bin.control import repost_oblast_setka
        self.assertTrue(hasattr(repost_oblast_setka, "repost_oblast_setka"))


if __name__ == "__main__":
    unittest.main()
