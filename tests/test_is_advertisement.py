"""Тесты для модуля определения рекламы."""

import unittest

from bin.utils.is_advertisement import (
    AD_SCORE_THRESHOLD,
    check_advertising_markers,
    check_commercial_patterns,
    check_vk_api_marked,
    is_advertisement,
)


class TestVkApiMarked(unittest.TestCase):

    def test_marked_as_ads_true(self):
        post = {"marked_as_ads": True}
        self.assertTrue(check_vk_api_marked(post))

    def test_marked_as_ads_false(self):
        post = {"marked_as_ads": False}
        self.assertFalse(check_vk_api_marked(post))

    def test_no_field(self):
        post = {"id": 123}
        self.assertFalse(check_vk_api_marked(post))


class TestAdvertisingMarkers(unittest.TestCase):

    def test_hashtag_reklama(self):
        self.assertTrue(check_advertising_markers("Текст #реклама ещё текст"))

    def test_hashtag_ad(self):
        self.assertTrue(check_advertising_markers("Текст #ad ещё текст"))

    def test_hashtag_sponsored(self):
        self.assertTrue(check_advertising_markers("Текст #sponsored"))

    def test_erid_token(self):
        self.assertTrue(check_advertising_markers("Текст erid: ABC12345678901234567890"))

    def test_na_pravakh_reklamy(self):
        self.assertTrue(check_advertising_markers("На правах рекламы"))

    def test_reklamnyy_material(self):
        self.assertTrue(check_advertising_markers("Рекламный материал"))

    def test_partnerstvo(self):
        self.assertTrue(check_advertising_markers("На правах партнёрства"))

    def test_no_markers(self):
        self.assertFalse(check_advertising_markers("Обычная новость без рекламы"))


class TestCommercialPatterns(unittest.TestCase):

    def test_skidka(self):
        score = check_commercial_patterns("Скидки до 50% только сегодня!")
        self.assertGreater(score, 0)

    def test_kupit(self):
        score = check_commercial_patterns("Купить можно по телефону +7-999-123-45-67")
        self.assertGreater(score, 0)

    def test_besplatno(self):
        score = check_commercial_patterns("Бесплатно при заказе сейчас")
        self.assertGreater(score, 0)

    def test_no_patterns(self):
        score = check_commercial_patterns("Вчера в городе прошла выставка")
        self.assertEqual(score, 0)


class TestIsAdvertisement(unittest.TestCase):

    def test_vk_marked_as_ads(self):
        post = {"marked_as_ads": True, "text": "Какой-то текст"}
        self.assertTrue(is_advertisement(post))

    def test_has_reklama_hashtag(self):
        post = {"text": "Отличная акция #реклама"}
        self.assertTrue(is_advertisement(post))

    def test_has_erid(self):
        post = {"text": "Текст erid: ABCDEFGHIJKLMNOP12345"}
        self.assertTrue(is_advertisement(post))

    def test_news_not_ad(self):
        """Обычная новость не должен считаться рекламой."""
        post = {
            "text": "Вчера в городе прошло мероприятие, собравшее много участников",
            "attachments": [],
        }
        self.assertFalse(is_advertisement(post))

    def test_cultural_event_not_ad(self):
        """Культурное мероприятие без рекламных маркеров."""
        post = {
            "text": "Приглашаем на выставку в музей современного искусства. Открытие в 18:00, вход свободный",
        }
        # "вход свободный" может дать 1 балл, но ниже порога
        self.assertFalse(is_advertisement(post))

    def test_clear_advertisement(self):
        """Явная реклама с маркерами."""
        post = {
            "text": "Скидки 50%! Звоните прямо сейчас: +7-999-123-45-67. #реклама",
        }
        self.assertTrue(is_advertisement(post))

    def test_high_score_without_hashtag(self):
        """Много коммерческих паттернов — выше порога даже без #реклама."""
        post = {
            "text": (
                "Скидка 40% на всё! Бесплатно при заказе. "
                "Звоните прямо сейчас: +7-999-123-45-67. "
                "Торопитесь, акция ограничена!"
            ),
        }
        self.assertTrue(is_advertisement(post))

    def test_threshold_value(self):
        """Порог должен быть 4."""
        self.assertEqual(AD_SCORE_THRESHOLD, 4)


if __name__ == "__main__":
    unittest.main()
