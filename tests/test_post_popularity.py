"""Тесты для модуля расчёта популярности постов."""

import unittest

from bin.utils.post_popularity import get_post_popularity_score


class TestPostPopularityScore(unittest.TestCase):

    def _make_post(self, views=0, likes=0, comments=0, reposts=0):
        return {
            "views": {"count": views},
            "likes": {"count": likes},
            "comments": {"count": comments},
            "reposts": {"count": reposts},
        }

    def test_zero_metrics(self):
        """Post with all zeros should have score 0."""
        post = self._make_post()
        self.assertEqual(get_post_popularity_score(post), 0.0)

    def test_views_only(self):
        """Post with only views but no engagement should have score 0."""
        post = self._make_post(views=1000)
        self.assertEqual(get_post_popularity_score(post), 0.0)

    def test_likes_increase_score(self):
        """More likes should increase score."""
        post_low = self._make_post(views=100, likes=5)
        post_high = self._make_post(views=100, likes=20)
        self.assertGreater(
            get_post_popularity_score(post_high),
            get_post_popularity_score(post_low),
        )

    def test_comments_weight_higher_than_likes(self):
        """One comment should be worth 2 likes."""
        post_with_like = self._make_post(views=100, likes=2)
        post_with_comment = self._make_post(views=100, comments=1)
        self.assertEqual(
            get_post_popularity_score(post_with_like),
            get_post_popularity_score(post_with_comment),
        )

    def test_reposts_weight_highest(self):
        """One repost should be worth 3 likes."""
        post_with_likes = self._make_post(views=100, likes=3)
        post_with_repost = self._make_post(views=100, reposts=1)
        self.assertEqual(
            get_post_popularity_score(post_with_likes),
            get_post_popularity_score(post_with_repost),
        )

    def test_high_engagement_rate_beats_high_views(self):
        """
        Post with fewer views but higher engagement rate should score higher
        than post with many views but low engagement.
        """
        # 200 views, 20 likes → 10% engagement rate
        post_engaged = self._make_post(views=200, likes=20)
        # 10000 views, 10 likes → 0.1% engagement rate
        post_viral = self._make_post(views=10000, likes=10)
        self.assertGreater(
            get_post_popularity_score(post_engaged),
            get_post_popularity_score(post_viral),
        )

    def test_missing_fields_handled_safely(self):
        """Post without likes/comments/reposts should not crash."""
        post = {"views": {"count": 100}}
        score = get_post_popularity_score(post)
        self.assertEqual(score, 0.0)

    def test_no_views_field(self):
        """Post without views should handle gracefully."""
        post = {"likes": {"count": 5}}
        score = get_post_popularity_score(post)
        # views defaults to 0, so score = 5 / sqrt(0 + 1) = 5.0
        self.assertEqual(score, 5.0)

    def test_empty_post(self):
        """Empty post should not crash."""
        post = {}
        score = get_post_popularity_score(post)
        self.assertEqual(score, 0.0)

    def test_sorting_order(self):
        """Posts should be sorted by popularity score correctly."""
        posts = [
            self._make_post(views=1000, likes=5),    # low engagement
            self._make_post(views=100, likes=20),    # high engagement
            self._make_post(views=500, likes=10),    # medium
        ]
        sorted_posts = sorted(posts, key=get_post_popularity_score, reverse=True)
        # Высокий engagement должен быть первым
        self.assertEqual(sorted_posts[0]["likes"]["count"], 20)


if __name__ == "__main__":
    unittest.main()
