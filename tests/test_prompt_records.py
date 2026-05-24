import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PromptRecordTests(unittest.TestCase):
    def test_prompt_token_usage_ledger_exists(self):
        ledger = ROOT / "prompts" / "token-usage.md"

        self.assertTrue(ledger.exists())

    def test_token_usage_ledger_has_current_prompt(self):
        ledger = (ROOT / "prompts" / "token-usage.md").read_text(encoding="utf-8")

        self.assertIn("prompt_token_usage_request", ledger)
        self.assertIn("estimated_prompt_tokens", ledger)
        self.assertIn("actual_prompt_tokens", ledger)


if __name__ == "__main__":
    unittest.main()
