from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor.cleaning import parse_document


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect normalized narrative blocks for a filing.")
    parser.add_argument("filing", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    content = args.filing.read_text(encoding="utf-8", errors="replace")
    document = parse_document(content)
    payload = {
        "path": str(args.filing),
        "clean_text_length": len(document.text),
        "block_count": len(document.blocks),
        "warnings": document.warnings,
        "blocks": [
            {
                "text": block.text[:240],
                "clean_start": block.clean_start,
                "clean_end": block.clean_end,
                "raw_start": block.raw_start,
                "raw_end": block.raw_end,
                "tag": block.tag,
                "source": block.source,
            }
            for block in document.blocks[: args.limit]
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
