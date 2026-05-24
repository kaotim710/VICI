from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_gold_boundaries import GOLD_PATH, evaluate_gold
from evaluate_seed import MANIFEST_PATH, SUMMARY_PATH, evaluate_seed, evaluation_summary


def main() -> int:
    seed_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    gold_manifest = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    seed_payload = evaluate_seed(seed_manifest)
    gold_payload = evaluate_gold(gold_manifest)
    summary = evaluation_summary(seed_payload, gold_payload)

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    return 0 if summary["evaluation_gate"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
