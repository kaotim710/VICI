import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_seed_extractions_md import _compact, _edge_snippets


class MarkdownReportTests(unittest.TestCase):
    def test_compact_collapses_whitespace_and_limits_length(self):
        compacted = _compact("alpha\n\nbeta   gamma", 12)

        self.assertEqual(compacted, "alpha bet...")

    def test_compact_escapes_table_delimiters(self):
        self.assertEqual(_compact("a | b ` c", 50), "a \\| b ' c")

    def test_edge_snippets_include_start_and_end(self):
        start, end = _edge_snippets("alpha beta gamma delta epsilon", 14)

        self.assertEqual(start, "alpha beta...")
        self.assertEqual(end, "...lta epsilon")


if __name__ == "__main__":
    unittest.main()
