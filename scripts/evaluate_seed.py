from __future__ import annotations

import json
import sys
from collections import Counter
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
    filing_status_counts = Counter()
    item_status_counts = Counter()
    confidence_level_counts = Counter()
    warning_counts = Counter()

    for filing in manifest["filings"]:
        path = RAW_DIR / f"{filing['filing_id']}.html"
        if not path.exists():
            missing.append(filing["filing_id"])
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        result = extract_items(content, target_items=manifest["items"], filing_id=filing["filing_id"])
        filing_status_counts[result.status] += 1
        for item in result.item_results:
            item_status_counts[item.status] += 1
            confidence_level_counts[item.confidence_level] += 1
            warning_counts.update(item.warnings)
        rows.append(
            {
                "filing_id": filing["filing_id"],
                "status": result.status,
                "candidate_count": result.candidate_count,
                "items": {
                    item.item: {
                        "status": item.status,
                        "confidence_level": item.confidence_level,
                        "confidence_score": item.confidence_score,
                        "text_length": len(item.text or ""),
                        "confidence_components": [
                            {
                                "name": component.name,
                                "earned": component.earned,
                                "weight": component.weight,
                                "passed": component.passed,
                            }
                            for component in item.confidence_components
                        ],
                        "warnings": item.warnings,
                    }
                    for item in result.item_results
                },
            }
        )

    payload = {
        "evaluated": len(rows),
        "missing": missing,
        "summary": {
            "filing_status_counts": dict(filing_status_counts),
            "item_status_counts": dict(item_status_counts),
            "confidence_level_counts": dict(confidence_level_counts),
            "warning_counts": dict(warning_counts),
        },
        "results": rows,
    }
    print(json.dumps(payload, indent=2))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
