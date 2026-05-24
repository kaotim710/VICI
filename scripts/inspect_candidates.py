from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor.candidates import find_heading_candidates
from sec_item_extractor.cleaning import parse_document


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect item heading candidates for a filing.")
    parser.add_argument("filing", type=Path)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    content = args.filing.read_text(encoding="utf-8", errors="replace")
    document = parse_document(content)
    candidates = find_heading_candidates(document.text, document.blocks)
    payload = {
        "path": str(args.filing),
        "candidate_count": len(candidates),
        "candidates": [
            {
                "item": candidate.item,
                "text": candidate.text,
                "clean_start": candidate.start,
                "clean_end": candidate.end,
                "raw_start": candidate.raw_start,
                "raw_end": candidate.raw_end,
                "block_index": candidate.block_index,
                "block_tag": candidate.block_tag,
                "is_toc_like": candidate.is_toc_like,
                "reasons": candidate.reasons,
            }
            for candidate in candidates[: args.limit]
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
