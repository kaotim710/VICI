from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor import extract_items


MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
RAW_DIR = ROOT / "fixtures" / "filings" / "raw"


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rows = []
    missing = []

    for filing in manifest["filings"]:
        path = RAW_DIR / f"{filing['filing_id']}.html"
        if not path.exists():
            missing.append(filing["filing_id"])
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        result = extract_items(content, target_items=manifest["items"], filing_id=filing["filing_id"])
        rows.append(
            {
                "filing_id": filing["filing_id"],
                "status": result.status,
                "items": {
                    item.item: {
                        "status": item.status,
                        "confidence_level": item.confidence_level,
                        "confidence_score": item.confidence_score,
                        "warnings": item.warnings,
                    }
                    for item in result.item_results
                },
            }
        )

    print(json.dumps({"evaluated": len(rows), "missing": missing, "results": rows}, indent=2))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())

