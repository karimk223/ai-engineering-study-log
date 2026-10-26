import json
import unittest
from unittest.mock import Mock, patch

from groq.types.chat import ChatCompletion

from automatic_agent import MAX_TOOL_CALLS, TOOL_FUNCTIONS, run_agent
from tools import multiply


def fake_reply(tool_name=None, text="Done.", call_id="test-call"):
    message = {"role": "assistant", "content": text}
    reason = "stop"

    if tool_name is not None:
        message = {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps({"a": 18, "b": 24}),
                    },
                }
            ],
        }
        reason = "tool_calls"

    return ChatCompletion(
        id="test-response",
        created=0,
        model="test-model",
        object="chat.completion",
        choices=[{"index": 0, "finish_reason": reason, "message": message}],
    )


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.tool = Mock(wraps=multiply)
        tool_patch = patch.dict(TOOL_FUNCTIONS, {"multiply": self.tool})
        tool_patch.start()
        self.addCleanup(tool_patch.stop)

    def test_returns_tool_result_to_model(self):
        self.client.chat.completions.create.side_effect = [
            fake_reply(tool_name="multiply"),
            fake_reply(text="There are 432 items."),
        ]

        answer = run_agent(self.client, "Test question")

        self.assertEqual(answer, "There are 432 items.")
        self.tool.assert_called_once_with(a=18, b=24)
        self.assertEqual(self.client.chat.completions.create.call_count, 2)

        messages = self.client.chat.completions.create.call_args.kwargs["messages"]
        self.assertEqual(
            messages[-1],
            {"role": "tool", "tool_call_id": "test-call", "content": "432"},
        )

    def test_accepts_answer_after_three_tools(self):
        replies = [
            fake_reply(tool_name="multiply", call_id=f"call-{i}")
            for i in range(MAX_TOOL_CALLS)
        ]
        self.client.chat.completions.create.side_effect = [
            *replies,
            fake_reply(text="Finished."),
        ]

        self.assertEqual(run_agent(self.client, "Test question"), "Finished.")
        self.assertEqual(self.tool.call_count, MAX_TOOL_CALLS)
        self.assertEqual(
            self.client.chat.completions.create.call_count, MAX_TOOL_CALLS + 1
        )

    def test_stops_before_fourth_tool(self):
        self.client.chat.completions.create.side_effect = [
            fake_reply(tool_name="multiply", call_id=f"call-{i}")
            for i in range(MAX_TOOL_CALLS + 1)
        ]

        with self.assertRaisesRegex(RuntimeError, "limit"):
            run_agent(self.client, "Test question")

        self.assertEqual(self.tool.call_count, MAX_TOOL_CALLS)
        self.assertEqual(
            self.client.chat.completions.create.call_count, MAX_TOOL_CALLS + 1
        )

    def test_rejects_unknown_tool(self):
        self.client.chat.completions.create.return_value = fake_reply(
            tool_name="unknown_tool"
        )

        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            run_agent(self.client, "Test question")

        self.tool.assert_not_called()


if __name__ == "__main__":
    unittest.main()