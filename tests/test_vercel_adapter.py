import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.index import handler
from sec_item_extractor.web_ui import WebUiHandler


class VercelAdapterTests(unittest.TestCase):
    def test_vercel_handler_reuses_web_ui_handler(self):
        self.assertTrue(issubclass(handler, WebUiHandler))


if __name__ == "__main__":
    unittest.main()
