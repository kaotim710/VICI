from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sec_item_extractor.web_ui import WebUiHandler


class handler(WebUiHandler):
    """Vercel Python Function entrypoint."""

