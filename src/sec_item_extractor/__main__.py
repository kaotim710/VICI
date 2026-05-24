from __future__ import annotations

import argparse
import json
from pathlib import Path

from .extractor import extract_items


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract SEC 10-K item sections.")
    parser.add_argument("filing", type=Path, help="Path to a local SEC 10-K HTML or text filing.")
    parser.add_argument("--items", nargs="+", default=["1", "1A", "7"], help="Items to extract.")
    args = parser.parse_args()

    content = args.filing.read_text(encoding="utf-8", errors="replace")
    result = extract_items(content, target_items=args.items, filing_id=args.filing.stem)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

