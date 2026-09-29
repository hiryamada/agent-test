import unittest
from unittest.mock import patch

import book_reviews


class BuildReviewPromptTests(unittest.TestCase):
    def test_prompt_includes_book_title_and_analysis_requirements(self):
        prompt = book_reviews.build_review_prompt("雪国")

        self.assertIn("「雪国」", prompt)
        self.assertIn("肯定・否定の傾向", prompt)
        self.assertIn("レビュー内容や件数を捏造しない", prompt)
        self.assertIn("情報源", prompt)

    def test_prompt_includes_author_when_provided(self):
        prompt = book_reviews.build_review_prompt("雪国", "川端康成")

        self.assertIn("著者: 川端康成", prompt)


class EnvironmentTests(unittest.TestCase):
    def test_missing_required_environment_variable_is_described(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "PROJECT_ENDPOINT"):
                book_reviews._required_environment("PROJECT_ENDPOINT")


if __name__ == "__main__":
    unittest.main()
