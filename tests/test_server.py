import unittest

from sec_item_extractor.server import PayloadError, extract_from_payload


class ServerPayloadTests(unittest.TestCase):
    def test_extracts_default_mvp_items_from_payload(self):
        payload = {
            "filing_id": "sample",
            "content": """
            Item 1. Business
            Business narrative long enough to pass the basic extraction path.
            """ + ("alpha " * 220) + """
            Item 1A. Risk Factors
            Risk narrative.
            """ + ("beta " * 220) + """
            Item 7. Management's Discussion and Analysis
            MD&A narrative.
            """ + ("gamma " * 220) + """
            Item 7A. Market Risk
            Market risk narrative.
            """,
        }

        result = extract_from_payload(payload)

        self.assertEqual(result["filing_id"], "sample")
        self.assertEqual([item["item"] for item in result["item_results"]], ["1", "1A", "7"])
        self.assertEqual(result["item_results"][0]["status"], "success")

    def test_rejects_empty_content(self):
        with self.assertRaises(PayloadError):
            extract_from_payload({"content": ""})

    def test_rejects_non_list_items(self):
        with self.assertRaises(PayloadError):
            extract_from_payload({"content": "Item 1. Business", "items": "1"})


if __name__ == "__main__":
    unittest.main()
