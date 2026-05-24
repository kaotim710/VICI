import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_seed_extractions_md import _compact


class MarkdownReportTests(unittest.TestCase):
    def test_compact_collapses_whitespace_and_limits_length(self):
        compacted = _compact("alpha\n\nbeta   gamma", 12)

        self.assertEqual(compacted, "alpha bet...")

    def test_compact_escapes_table_delimiters(self):
        self.assertEqual(_compact("a | b ` c", 50), "a \\| b ' c")


if __name__ == "__main__":
    unittest.main()
