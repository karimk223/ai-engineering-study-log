import unittest

from ollama_demo import get_reply


class OllamaReplyTests(unittest.TestCase):
    def setUp(self):
        self.result = {
            "done": True,
            "done_reason": "stop",
            "eval_count": 10,
            "message": {"content": "Example reply."},
        }

    def test_accepts_complete_reply(self):
        self.assertEqual(get_reply(self.result), "Example reply.")

    def test_rejects_unfinished_reply(self):
        self.result["done"] = False

        with self.assertRaisesRegex(RuntimeError, "done=False"):
            get_reply(self.result)

    def test_rejects_token_limit(self):
        self.result["done_reason"] = "length"
        self.result["eval_count"] = 256

        with self.assertRaisesRegex(RuntimeError, "reason=length"):
            get_reply(self.result)

    def test_rejects_blank_reply(self):
        for text in ["", "   ", None]:
            with self.subTest(text=text):
                self.result["message"]["content"] = text

                with self.assertRaisesRegex(RuntimeError, "no reply text"):
                    get_reply(self.result)


if __name__ == "__main__":
    unittest.main()