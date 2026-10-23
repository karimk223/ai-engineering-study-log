import unittest
from unittest.mock import Mock

from sentiment_demo import validate_texts


class SentimentInputTests(unittest.TestCase):
    def test_accepts_short_text(self):
        tokenizer = Mock(
            return_value={"input_ids": [0] * 10}
        )

        self.assertIsNone(
            validate_texts(["A movie review."], tokenizer)
        )

        tokenizer.assert_called_once_with(
            "A movie review.",
            truncation=False,
            verbose=False,
        )

    def test_rejects_blank_text(self):
        for text in ["", "   "]:
            with self.subTest(text=text):
                tokenizer = Mock()

                with self.assertRaisesRegex(
                    ValueError, "Text 1 is empty"
                ):
                    validate_texts([text], tokenizer)

                tokenizer.assert_not_called()

    def test_accepts_512_tokens(self):
        tokenizer = Mock(
            return_value={"input_ids": [0] * 512}
        )

        self.assertIsNone(
            validate_texts(["A movie review."], tokenizer)
        )

    def test_rejects_513_tokens(self):
        tokenizer = Mock(
            return_value={"input_ids": [0] * 513}
        )

        with self.assertRaisesRegex(
            ValueError,
            "Text 1 has 513 tokens; maximum is 512",
        ):
            validate_texts(["A movie review."], tokenizer)


if __name__ == "__main__":
    unittest.main()