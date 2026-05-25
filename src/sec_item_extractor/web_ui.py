from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
import hashlib
from html import unescape
import json
import mimetypes
import os
import re
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .candidates import ITEM_ORDER, SEC_ITEM_TITLES, is_expected_title
from .extractor import extract_items
from .raw_structure import (
    raw_fragment_exhibit_links,
    raw_fragment_internal_toc_chunk,
    raw_fragment_outline,
    raw_fragment_outline_sections,
    raw_fragment_supplemental_fragment,
    raw_fragment_structure,
    raw_fragment_supplemental_chunk,
    raw_section_fragment,
    raw_section_srcdoc,
    raw_structure_counts,
)
from .recovery import run_recovery_actions
from .sec_client import SECClient, archive_url, format_cik


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "fixtures" / "gold" / "seed_filings.json"
INVENTORY_PATH = ROOT / "fixtures" / "gold" / "downloaded_seed_filings.json"
RAW_DIR = ROOT / "fixtures" / "filings" / "raw"
FRONTEND_DIR = ROOT / "frontend"
LIVE_SMOKE_SUMMARY_PATH = ROOT / "reports" / "live_sec_smoke_summary.json"
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", str(25 * 1024 * 1024)))


def filing_options() -> list[dict]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    options = []
    for filing in manifest["filings"]:
        path = RAW_DIR / f"{filing['filing_id']}.html"
        options.append(
            {
                "filing_id": filing["filing_id"],
                "ticker": filing["ticker"],
                "fiscal_year": filing["fiscal_year"],
                "industry": filing["industry"],
                "form": filing["form"],
                "available": path.exists(),
                "bytes": path.stat().st_size if path.exists() else None,
            }
        )
    return options


def live_smoke_data() -> dict:
    if not LIVE_SMOKE_SUMMARY_PATH.exists():
        return {
            "available": False,
            "path": str(LIVE_SMOKE_SUMMARY_PATH.relative_to(ROOT)),
            "summary": None,
            "filings": [],
        }
    payload = json.loads(LIVE_SMOKE_SUMMARY_PATH.read_text(encoding="utf-8"))
    payload["available"] = True
    payload["path"] = str(LIVE_SMOKE_SUMMARY_PATH.relative_to(ROOT))
    return payload


def raw_filing_metadata(filing_id: str) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    filings = {filing["filing_id"]: filing for filing in manifest["filings"]}
    if filing_id not in filings:
        raise KeyError(filing_id)

    path = RAW_DIR / f"{filing_id}.html"
    if not path.exists():
        raise FileNotFoundError(path)

    inventory = _inventory_by_filing_id()
    record = inventory.get(filing_id, {})
    return {
        "filing": filings[filing_id],
        "raw": {
            "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "sha256": record.get("sha256") or _sha256(path),
        },
        "cache_policy": "no-store",
    }


def sec_intake_plan(ticker: str = "", cik: str = "", fiscal_year: int | str | None = None) -> dict:
    year = _parse_fiscal_year(fiscal_year)
    ticker = ticker.strip().upper()
    cik = cik.strip()
    if not ticker and not cik:
        raise ValueError("ticker or cik is required")

    payload = {
        "query": {"ticker": ticker or None, "cik": cik or None, "fiscal_year": year},
        "storage_policy": _direct_fetch_storage_policy(),
        "rate_limit": {"requests_per_second": 10, "user_agent_required": True},
        "status": "blocked",
        "message": "SEC_USER_AGENT is required before live SEC requests can run.",
    }
    user_agent = os.environ.get("SEC_USER_AGENT", "").strip()
    if not user_agent:
        return payload

    client = SECClient(user_agent=user_agent)
    resolved_cik = format_cik(cik) if cik else None
    resolved_ticker = None
    company_title = None
    if ticker:
        match = client.lookup_ticker(ticker)
        if match is None:
            return payload | {"status": "not_found", "message": f"No SEC ticker directory match for {ticker}."}
        resolved_cik = match.cik
        resolved_ticker = match.ticker
        company_title = match.title

    filing = client.find_10k_for_year(resolved_cik, year)
    if filing is None:
        return payload | {
            "status": "not_found",
            "message": f"No 10-K found for CIK {resolved_cik} with report date in {year}.",
            "company": {"ticker": resolved_ticker, "title": company_title, "cik": resolved_cik},
        }

    return payload | {
        "status": "ready",
        "message": "10-K metadata resolved. Filing can be fetched directly without writing raw storage.",
        "company": {"ticker": resolved_ticker, "title": company_title, "cik": resolved_cik},
        "filing": {
            "accession_number": filing.accession_number,
            "filing_date": filing.filing_date,
            "report_date": filing.report_date,
            "primary_document": filing.primary_document,
            "download_url": archive_url(resolved_cik, filing.accession_number, filing.primary_document),
        },
    }


def extract_sec_filing(ticker: str = "", cik: str = "", fiscal_year: int | str | None = None) -> dict:
    year = _parse_fiscal_year(fiscal_year)
    ticker = ticker.strip().upper()
    cik = cik.strip()
    if not ticker and not cik:
        raise ValueError("ticker or cik is required")

    user_agent = os.environ.get("SEC_USER_AGENT", "").strip()
    if not user_agent:
        return {
            "query": {"ticker": ticker or None, "cik": cik or None, "fiscal_year": year},
            "status": "blocked",
            "message": "SEC_USER_AGENT is required before live SEC requests can run.",
            "storage_policy": _direct_fetch_storage_policy(),
        }

    started = time.perf_counter()
    client = SECClient(user_agent=user_agent)
    resolved_cik = format_cik(cik) if cik else None
    resolved_ticker = ticker or None
    company_title = None
    if ticker:
        match = client.lookup_ticker(ticker)
        if match is None:
            return {
                "query": {"ticker": ticker, "cik": None, "fiscal_year": year},
                "status": "not_found",
                "message": f"No SEC ticker directory match for {ticker}.",
                "storage_policy": _direct_fetch_storage_policy(),
            }
        resolved_cik = match.cik
        resolved_ticker = match.ticker
        company_title = match.title

    download = client.download_10k_for_year(resolved_cik, year)
    if download is None:
        return {
            "query": {"ticker": resolved_ticker, "cik": resolved_cik, "fiscal_year": year},
            "status": "not_found",
            "message": f"No 10-K found for CIK {resolved_cik} with report date in {year}.",
            "storage_policy": _direct_fetch_storage_policy(),
        }

    content = download.body.decode("utf-8", errors="replace")
    filing_id = f"sec_{resolved_ticker or resolved_cik}_{year}_10k".lower()
    result = extract_items(content, target_items=ITEM_ORDER, filing_id=filing_id)
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    result_dict = result.to_dict()
    _attach_raw_structure(result_dict, content, result.item_results, raw_section_available=False)
    _append_supplemental_items(result_dict, raw_section_available=False)
    _attach_live_raw_sections(result_dict, content, result.item_results, download.archive_url)
    _attach_sec_item_format(result_dict)
    warning_count = sum(len(item.get("warnings", [])) for item in result_dict.get("item_results", []))
    action_count = sum(len(item.get("recommended_actions", [])) for item in result_dict.get("item_results", []))
    sec_format_review_count = _sec_format_review_count(result_dict)
    return {
        "query": {"ticker": resolved_ticker, "cik": resolved_cik, "fiscal_year": year},
        "filing": {
            "filing_id": filing_id,
            "ticker": resolved_ticker,
            "title": company_title,
            "cik": resolved_cik,
            "fiscal_year": year,
            "form": download.metadata.form,
            "accession_number": download.metadata.accession_number,
            "filing_date": download.metadata.filing_date,
            "report_date": download.metadata.report_date,
            "primary_document": download.metadata.primary_document,
            "download_url": download.archive_url,
        },
        "elapsed_ms": elapsed_ms,
        "source_bytes": len(download.body),
        "status": "success",
        "message": "10-K downloaded from SEC and extracted in memory without raw persistence.",
        "storage_policy": _direct_fetch_storage_policy(),
        "pipeline": {
            "ran": True,
            "cache": "disabled",
            "trigger": "live_sec_direct_fetch_extract",
            "parser_version": result.parser_version,
        },
        "summary": {
            "status": result.status,
            "candidate_count": result.candidate_count,
            "toc_confidence": result.toc_confidence,
            "item_count": len(result_dict.get("item_results", [])),
            "warning_count": warning_count,
            "recommended_action_count": action_count,
            "sec_format_review_count": sec_format_review_count,
        },
        "result": result_dict,
    }


def extract_uploaded_filing(file_bytes: bytes, filename: str) -> dict:
    if not file_bytes:
        raise ValueError("uploaded filing file is required")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError(f"uploaded filing exceeds {MAX_UPLOAD_BYTES} byte limit")

    safe_filename = _safe_filename(filename or "uploaded-filing.html")
    content = file_bytes.decode("utf-8", errors="replace")
    if not content.strip():
        raise ValueError("uploaded filing file is empty")

    started = time.perf_counter()
    inferred = infer_upload_metadata(content, safe_filename)
    digest = hashlib.sha256(file_bytes).hexdigest()
    filing_id = f"upload_{_slug(safe_filename)}_{digest[:12]}"
    result = extract_items(content, target_items=ITEM_ORDER, filing_id=filing_id)
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    result_dict = result.to_dict()
    _attach_raw_structure(result_dict, content, result.item_results, raw_section_available=False)
    _append_supplemental_items(result_dict, raw_section_available=False)
    _attach_live_raw_sections(result_dict, content, result.item_results, None)
    _attach_sec_item_format(result_dict)
    warning_count = sum(len(item.get("warnings", [])) for item in result_dict.get("item_results", []))
    action_count = sum(len(item.get("recommended_actions", [])) for item in result_dict.get("item_results", []))
    sec_format_review_count = _sec_format_review_count(result_dict)
    return {
        "query": {"ticker": inferred["ticker"], "fiscal_year": inferred["fiscal_year"]},
        "filing": {
            "filing_id": filing_id,
            "ticker": inferred["ticker"],
            "title": inferred["registrant_name"] or safe_filename,
            "cik": inferred["cik"],
            "fiscal_year": inferred["fiscal_year"],
            "form": inferred["form"],
            "accession_number": None,
            "filing_date": None,
            "report_date": None,
            "primary_document": safe_filename,
            "download_url": None,
        },
        "inferred_metadata": inferred,
        "elapsed_ms": elapsed_ms,
        "source_bytes": len(file_bytes),
        "source_sha256": digest,
        "status": "success",
        "message": "Uploaded filing extracted in memory without raw persistence.",
        "storage_policy": _direct_fetch_storage_policy(),
        "pipeline": {
            "ran": True,
            "cache": "disabled",
            "trigger": "uploaded_filing_extract",
            "parser_version": result.parser_version,
        },
        "summary": {
            "status": result.status,
            "candidate_count": result.candidate_count,
            "toc_confidence": result.toc_confidence,
            "item_count": len(result_dict.get("item_results", [])),
            "warning_count": warning_count,
            "recommended_action_count": action_count,
            "sec_format_review_count": sec_format_review_count,
        },
        "result": result_dict,
    }


def identify_uploaded_filing(
    file_bytes: bytes,
    filename: str,
    *,
    original_size: int | None = None,
    partial_upload: bool = False,
) -> dict:
    if not file_bytes:
        raise ValueError("uploaded filing file is required")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError(f"uploaded filing identification exceeds {MAX_UPLOAD_BYTES} byte limit")

    safe_filename = _safe_filename(filename or "uploaded-filing.html")
    content = file_bytes.decode("utf-8", errors="replace")
    if not content.strip():
        raise ValueError("uploaded filing file is empty")

    inferred = infer_upload_metadata(content, safe_filename)
    digest = hashlib.sha256(file_bytes).hexdigest()
    form = inferred["form"]
    is_10k = form is None or form.startswith("10-K")
    identifier_key = "ticker" if inferred["ticker"] else "cik"
    identifier = inferred["ticker"] or inferred["cik"]
    ready = bool(identifier and inferred["fiscal_year"] and is_10k)
    params = f"{identifier_key}={identifier}&year={inferred['fiscal_year']}" if identifier and inferred["fiscal_year"] else ""
    payload = {
        "query": {"ticker": inferred["ticker"], "fiscal_year": inferred["fiscal_year"]},
        "filing": {
            "filing_id": f"identified_{_slug(safe_filename)}_{digest[:12]}",
            "ticker": inferred["ticker"],
            "title": inferred["registrant_name"] or safe_filename,
            "cik": inferred["cik"],
            "fiscal_year": inferred["fiscal_year"],
            "form": inferred["form"],
            "accession_number": None,
            "filing_date": None,
            "report_date": None,
            "primary_document": safe_filename,
            "download_url": None,
        },
        "inferred_metadata": inferred,
        "source_bytes": len(file_bytes),
        "original_size": original_size,
        "partial_upload": partial_upload,
        "source_sha256": digest,
        "status": "ready" if ready else "needs_user_input",
        "message": (
            "Uploaded filing metadata identified. Continue with live SEC extraction."
            if ready
            else "Could not identify enough 10-K metadata from the uploaded file sample."
        ),
        "storage_policy": _direct_fetch_storage_policy(),
        "pipeline": {
            "ran": False,
            "cache": "disabled",
            "trigger": "uploaded_filing_identify",
        },
        "next_action": {
            "type": "live_sec_extract",
            "url": f"/sec-live?{params}",
        }
        if ready
        else None,
    }
    return payload


def _attach_sec_item_format(result_dict: dict) -> None:
    for item_payload in result_dict.get("item_results", []):
        item_payload["sec_item_format"] = _sec_item_format_contract(item_payload)


def _sec_format_review_count(result_dict: dict) -> int:
    review_statuses = {"noncanonical_heading", "label_only", "missing"}
    return sum(
        1
        for item in result_dict.get("item_results", [])
        if item.get("sec_item_format", {}).get("status") in review_statuses
    )


def _sec_item_format_contract(item_payload) -> dict:
    item_name = str(_payload_value(item_payload, "item", "")).upper()
    if item_name.startswith("SUPPLEMENTAL-"):
        source_item = item_name.removeprefix("SUPPLEMENTAL-")
        return {
            "applies_to_sec_item": False,
            "item": item_name,
            "sec_item_label": f"Supplemental after Item {source_item}",
            "expected_title": None,
            "start_heading": None,
            "heading_context": None,
            "label_matches": False,
            "title_matches_expected": False,
            "status": "virtual_partition",
            "notes": ["Supplemental partitions are same-filing review chunks, not SEC Form 10-K item headings."],
        }

    expected_title = SEC_ITEM_TITLES.get(item_name)
    start_evidence = _payload_value(item_payload, "start_evidence")
    start_heading = _payload_value(start_evidence, "text") if start_evidence else None
    heading_context = _heading_context(item_payload, start_heading)
    label_matches = _sec_label_matches(item_name, heading_context)
    title_matches = bool(expected_title and is_expected_title(item_name, heading_context))
    reasons = _payload_value(start_evidence, "reasons", []) if start_evidence else []
    status = _sec_format_status(item_payload, label_matches, title_matches, reasons, expected_title)
    notes = _sec_format_notes(item_payload, status, label_matches, title_matches, reasons, expected_title)
    return {
        "applies_to_sec_item": expected_title is not None,
        "item": item_name,
        "sec_item_label": f"Item {item_name}" if expected_title else item_name,
        "expected_title": expected_title,
        "start_heading": start_heading,
        "heading_context": heading_context or None,
        "label_matches": label_matches,
        "title_matches_expected": title_matches,
        "status": status,
        "source": _sec_format_source(reasons),
        "notes": notes,
    }


def _sec_format_status(item_payload, label_matches: bool, title_matches: bool, reasons: list, expected_title: str | None) -> str:
    if expected_title is None:
        return "unsupported_item"
    if _payload_value(item_payload, "status") != "success":
        return "missing"
    if title_matches and _is_cross_reference_fallback(reasons):
        return "fallback_canonical_match"
    if label_matches and title_matches:
        return "canonical_match"
    if label_matches:
        return "label_only"
    return "noncanonical_heading"


def _sec_format_notes(
    item_payload, status: str, label_matches: bool, title_matches: bool, reasons: list, expected_title: str | None
) -> list[str]:
    notes = []
    if expected_title is None:
        notes.append("No SEC canonical title is configured for this virtual or unsupported item.")
    elif _payload_value(item_payload, "status") != "success":
        notes.append("Item was not extracted, so the canonical heading could not be verified.")
    else:
        if not label_matches:
            notes.append("Extracted start context does not show a clear Item label.")
        if not title_matches:
            notes.append("Extracted start context does not contain the expected SEC canonical title tokens.")
        if _is_cross_reference_fallback(reasons):
            notes.append("Start was recovered from a Form 10-K cross-reference index page mapping.")
        if status == "canonical_match":
            notes.append("Start context includes the SEC item label and expected canonical title.")
    return notes


def _sec_format_source(reasons: list) -> str:
    if _is_cross_reference_fallback(reasons):
        return "cross_reference_page_fallback"
    if "REGEX_ITEM_HEADING" in reasons:
        return "body_heading"
    return "none"


def _is_cross_reference_fallback(reasons: list) -> bool:
    return any(str(reason).startswith("CROSS_REFERENCE_") for reason in reasons or [])


def _heading_context(item_payload, start_heading: str | None) -> str:
    text = _payload_value(item_payload, "text", "") or ""
    first_text = "\n".join(str(text).splitlines()[:4])
    return " ".join(part for part in [start_heading or "", first_text[:700]] if part).strip()


def _sec_label_matches(item_name: str, heading_context: str) -> bool:
    if not item_name or not heading_context:
        return False
    return bool(re.search(rf"(?i)\bitem\s+{re.escape(item_name)}(?![a-z0-9])", heading_context))


def _payload_value(payload, key: str, default=None):
    if isinstance(payload, dict):
        return payload.get(key, default)
    return getattr(payload, key, default)


def _direct_fetch_storage_policy() -> dict:
    return {
        "raw_storage_required": False,
        "default_mode": "direct_fetch_then_extract",
        "persist_raw_option": "available_for_evaluation_artifacts",
    }


def _attach_live_raw_sections(result_dict: dict, content: str, item_results: list, base_url: str | None) -> None:
    source_by_item = {item.item.upper(): item for item in item_results}
    for item_payload in result_dict.get("item_results", []):
        item_payload["live_raw_section_available"] = False
        source = source_by_item.get(str(item_payload.get("item", "")).upper())
        if source is None or source.status != "success":
            continue
        try:
            start, end, fragment = raw_section_fragment(content, source)
        except ValueError:
            continue
        structure = raw_fragment_structure(fragment)
        item_payload["live_raw_section_available"] = True
        item_payload["live_raw_section"] = {
            "raw_start": start,
            "raw_end": end,
            "raw_bytes": len(fragment.encode("utf-8", errors="replace")),
            "table_count": structure["table_count"],
            "image_count": structure["image_count"],
            "srcdoc": raw_section_srcdoc(fragment, base_url),
        }


def _parse_fiscal_year(value: int | str | None) -> int:
    if value is None:
        raise ValueError("fiscal_year is required")
    raw = str(value).strip()
    if not re.fullmatch(r"\d{4}", raw):
        raise ValueError("fiscal_year must be a four-digit year")
    return int(raw)


def _parse_optional_fiscal_year(value: int | str | None) -> int | None:
    if value is None or str(value).strip() == "":
        return None
    return _parse_fiscal_year(value)


def infer_upload_metadata(content: str, filename: str) -> dict:
    ticker, ticker_source = _infer_upload_ticker(content, filename)
    cik, cik_source = _infer_upload_cik(content)
    fiscal_year, fiscal_year_source = _infer_upload_fiscal_year(content, filename)
    form, form_source = _infer_upload_form(content, filename)
    registrant_name, registrant_source = _infer_dei_text(content, "EntityRegistrantName")
    return {
        "ticker": ticker,
        "ticker_source": ticker_source,
        "cik": cik,
        "cik_source": cik_source,
        "fiscal_year": fiscal_year,
        "fiscal_year_source": fiscal_year_source,
        "form": form,
        "form_source": form_source,
        "registrant_name": registrant_name,
        "registrant_name_source": registrant_source,
    }


def _infer_upload_ticker(content: str, filename: str) -> tuple[str | None, str]:
    value, source = _infer_dei_text(content, "TradingSymbol")
    if value:
        symbol = re.split(r"[\s,/]+", value.strip().upper())[0]
        if re.fullmatch(r"[A-Z][A-Z0-9.-]{0,9}", symbol):
            return symbol, source

    cover = _text_sample(content, 120000)
    match = re.search(r"trading\s+symbol(?:\(s\))?\s+([A-Z][A-Z0-9.-]{0,9})\b", cover, flags=re.IGNORECASE)
    if match:
        return match.group(1).upper(), "cover_page"

    filename_match = re.match(r"(?P<ticker>[a-zA-Z]{1,6})[_-]\d{4}[_-]10k\b", filename)
    if filename_match:
        return filename_match.group("ticker").upper(), "filename"
    return None, "not_found"


def _infer_upload_cik(content: str) -> tuple[str | None, str]:
    value, source = _infer_dei_text(content, "EntityCentralIndexKey")
    if value:
        digits = re.sub(r"\D+", "", value)
        if 1 <= len(digits) <= 10:
            return format_cik(digits), source
    return None, "not_found"


def _infer_upload_fiscal_year(content: str, filename: str) -> tuple[int | None, str]:
    value, source = _infer_dei_text(content, "DocumentFiscalYearFocus")
    if value and re.fullmatch(r"\d{4}", value.strip()):
        return int(value), source

    period_end, period_source = _infer_dei_text(content, "DocumentPeriodEndDate")
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", period_end or "")
    if year_match:
        return int(year_match.group(1)), period_source

    filename_match = re.search(r"(?<!\d)(19\d{2}|20\d{2})(?!\d)", filename)
    if filename_match:
        return int(filename_match.group(1)), "filename"
    return None, "not_found"


def _infer_upload_form(content: str, filename: str) -> tuple[str | None, str]:
    value, source = _infer_dei_text(content, "DocumentType")
    if value:
        form = value.strip().upper()
        if re.fullmatch(r"10-K(?:/A)?|10-Q(?:/A)?|20-F(?:/A)?|40-F(?:/A)?", form):
            return form, source

    sample = _text_sample(content, 60000)
    match = re.search(r"\bFORM\s+(10-K(?:/A)?|10-Q(?:/A)?|20-F(?:/A)?|40-F(?:/A)?)\b", sample, flags=re.IGNORECASE)
    if match:
        return match.group(1).upper(), "cover_page"
    if re.search(r"10[_-]?k", filename, flags=re.IGNORECASE):
        return "10-K", "filename"
    return None, "not_found"


def _infer_dei_text(content: str, concept: str) -> tuple[str | None, str]:
    pattern = (
        rf"(?is)<ix:(?:nonNumeric|nonFraction)\b"
        rf"(?=[^>]*\bname=[\"']dei:{re.escape(concept)}[\"'])[^>]*>(.*?)</ix:(?:nonNumeric|nonFraction)>"
    )
    match = re.search(pattern, content)
    if not match:
        return None, "not_found"
    value = _html_text(match.group(1))
    return (value or None), f"ixbrl_dei:{concept}"


def _text_sample(content: str, limit: int) -> str:
    return _html_text(content[:limit])


def _html_text(value: str) -> str:
    value = re.sub(r"(?is)<[^>]+>", " ", value)
    value = unescape(value)
    return " ".join(value.split())


def _safe_filename(value: str) -> str:
    name = Path(value).name.strip()
    return name or "uploaded-filing.html"


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return slug[:60] or "filing"


def extract_seed_filing(filing_id: str) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    filings = {filing["filing_id"]: filing for filing in manifest["filings"]}
    if filing_id not in filings:
        raise KeyError(filing_id)

    path = RAW_DIR / f"{filing_id}.html"
    if not path.exists():
        raise FileNotFoundError(path)

    started = time.perf_counter()
    content = path.read_text(encoding="utf-8", errors="replace")
    result = extract_items(content, target_items=manifest["items"], filing_id=filing_id)
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    result_dict = result.to_dict()
    _attach_raw_structure(result_dict, content, result.item_results)
    _append_supplemental_items(result_dict)
    _attach_sec_item_format(result_dict)
    item_count = len(result_dict.get("item_results", []))
    return {
        "filing": filings[filing_id],
        "elapsed_ms": elapsed_ms,
        "source_bytes": path.stat().st_size,
        "pipeline": {
            "ran": True,
            "cache": "disabled",
            "trigger": "on_demand_extract_request",
            "parser_version": result.parser_version,
        },
        "summary": {
            "status": result.status,
            "candidate_count": result.candidate_count,
            "toc_confidence": result.toc_confidence,
            "item_count": item_count,
        },
        "toc_entries": result_dict["toc_entries"],
        "items": [_item_contract(item, content) for item in result.item_results],
        "result": result_dict,
    }


def recover_seed_filing(filing_id: str, selections: dict[tuple[str | None, str], str] | None = None) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    filings = {filing["filing_id"]: filing for filing in manifest["filings"]}
    if filing_id not in filings:
        raise KeyError(filing_id)

    path = RAW_DIR / f"{filing_id}.html"
    if not path.exists():
        raise FileNotFoundError(path)

    started = time.perf_counter()
    content = path.read_text(encoding="utf-8", errors="replace")
    extraction = extract_items(content, target_items=manifest["items"], filing_id=filing_id)
    recoveries = run_recovery_actions(content, extraction, selections=selections)
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    return {
        "filing": filings[filing_id],
        "elapsed_ms": elapsed_ms,
        "pipeline": {
            "ran": True,
            "cache": "disabled",
            "trigger": "on_demand_recovery_request",
            "parser_version": extraction.parser_version,
        },
        "summary": {
            "status": extraction.status,
            "recovery_actions": len(recoveries),
        },
        "recoveries": [recovery.to_dict() for recovery in recoveries],
    }


def raw_section_preview(filing_id: str, item: str) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    filings = {filing["filing_id"]: filing for filing in manifest["filings"]}
    if filing_id not in filings:
        raise KeyError(filing_id)

    path = RAW_DIR / f"{filing_id}.html"
    if not path.exists():
        raise FileNotFoundError(path)

    item = item.upper()
    content = path.read_text(encoding="utf-8", errors="replace")
    if item.startswith("SUPPLEMENTAL-"):
        return _supplemental_raw_section_preview(filings[filing_id], filing_id, item, content)
    item, section_index = _parse_item_preview_item(item)
    result = extract_items(content, target_items=[item], filing_id=filing_id)
    item_result = result.item_results[0]
    if item_result.status != "success" or not item_result.start_evidence:
        raise ValueError(f"raw section is unavailable for Item {item}")

    start, _, item_fragment = raw_section_fragment(content, item_result)
    section_label = None
    if section_index is None:
        fragment = item_fragment
        section_relative_start = 0
    else:
        raw_structure = _raw_structure_contract(content, item_result)
        sections = raw_structure.get("sections", [])
        if section_index < 0 or section_index >= len(sections):
            raise ValueError(f"raw section is unavailable for Item {item}")
        section = sections[section_index]
        raw_start = int(section.get("raw_start", 0))
        raw_end = int(section.get("raw_end", 0))
        if raw_end <= raw_start:
            raise ValueError(f"raw section is unavailable for Item {item}")
        fragment = item_fragment[raw_start:raw_end]
        section_relative_start = raw_start
        section_label = section.get("label")
    start = start + section_relative_start
    end = start + len(fragment)
    base_url = _archive_base_url(filing_id)
    structure = raw_fragment_structure(fragment)
    return {
        "filing": filings[filing_id],
        "item": item,
        "section_label": section_label,
        "raw_start": start,
        "raw_end": end,
        "raw_bytes": len(fragment.encode("utf-8", errors="replace")),
        "table_count": structure["table_count"],
        "image_count": structure["image_count"],
        "base_url": base_url,
        "srcdoc": raw_section_srcdoc(fragment, base_url),
    }


def _supplemental_raw_section_preview(filing: dict, filing_id: str, item: str, content: str) -> dict:
    source_item, section_index = _parse_supplemental_preview_item(item)
    result = extract_items(content, target_items=[source_item], filing_id=filing_id)
    item_result = result.item_results[0]
    if item_result.status != "success" or not item_result.start_evidence:
        raise ValueError(f"raw section is unavailable for Item {item}")

    source_start, _, source_fragment = raw_section_fragment(content, item_result)
    supplemental = raw_fragment_supplemental_fragment(source_fragment)
    if supplemental is None:
        raise ValueError(f"raw section is unavailable for Item {item}")
    relative_start, supplemental_fragment = supplemental
    section_label = None
    if section_index is None:
        fragment = supplemental_fragment
        section_relative_start = 0
    else:
        chunk = raw_fragment_supplemental_chunk(source_fragment)
        sections = chunk.get("sections", []) if chunk else []
        if section_index < 0 or section_index >= len(sections):
            raise ValueError(f"raw section is unavailable for Item {item}")
        section = sections[section_index]
        raw_start = int(section.get("raw_start", 0))
        raw_end = int(section.get("raw_end", 0))
        if raw_end <= raw_start:
            raise ValueError(f"raw section is unavailable for Item {item}")
        fragment = supplemental_fragment[raw_start:raw_end]
        section_relative_start = raw_start
        section_label = section.get("label")
    start = source_start + relative_start + section_relative_start
    end = start + len(fragment)
    base_url = _archive_base_url(filing_id)
    structure = raw_fragment_structure(fragment)
    return {
        "filing": filing,
        "item": item,
        "section_label": section_label,
        "raw_start": start,
        "raw_end": end,
        "raw_bytes": len(fragment.encode("utf-8", errors="replace")),
        "table_count": structure["table_count"],
        "image_count": structure["image_count"],
        "base_url": base_url,
        "srcdoc": raw_section_srcdoc(fragment, base_url),
    }


def _parse_supplemental_preview_item(item: str) -> tuple[str, int | None]:
    source_item = item.removeprefix("SUPPLEMENTAL-")
    return _parse_item_preview_item(source_item)


def _parse_item_preview_item(item: str) -> tuple[str, int | None]:
    if ":" not in item:
        return item, None
    source_item, raw_index = item.split(":", 1)
    if not raw_index.isdigit():
        raise ValueError(f"raw section is unavailable for Item {item}")
    return source_item, int(raw_index)


def _item_contract(item, raw_content: str | None = None) -> dict:
    raw_structure = _raw_structure_contract(raw_content, item) if raw_content is not None else {"table_count": 0, "image_count": 0}
    return {
        "item": item.item,
        "status": item.status,
        "confidence": {"level": item.confidence_level, "score": item.confidence_score},
        "warnings": item.warnings,
        "actions": [action.__dict__ for action in item.recommended_actions],
        "evidence": {
            "start": item.start_evidence.__dict__ if item.start_evidence else None,
            "end": item.end_evidence.__dict__ if item.end_evidence else None,
        },
        "text": item.text or "",
        "text_length": len(item.text or ""),
        "raw_structure": raw_structure,
        "sec_item_format": _sec_item_format_contract(item.__dict__),
    }


def _inventory_by_filing_id() -> dict[str, dict]:
    if not INVENTORY_PATH.exists():
        return {}
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    return {record["filing_id"]: record for record in inventory.get("files", [])}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_recovery_selections(payload: dict, filing_id: str) -> dict[tuple[str | None, str], str]:
    raw_selections = payload.get("selections", {}) if isinstance(payload, dict) else {}
    if not isinstance(raw_selections, dict):
        return {}
    selections: dict[tuple[str | None, str], str] = {}
    for raw_key, raw_value in raw_selections.items():
        if not isinstance(raw_key, str) or not isinstance(raw_value, str) or not raw_value.strip():
            continue
        if ":" in raw_key:
            selected_filing, item = raw_key.split(":", 1)
            selections[(selected_filing or filing_id, item.upper())] = raw_value
        else:
            selections[(filing_id, raw_key.upper())] = raw_value
    return selections


def _archive_base_url(filing_id: str) -> str | None:
    record = _inventory_by_filing_id().get(filing_id)
    if not record:
        return None
    cik = record.get("cik")
    accession = record.get("accession_number")
    if not cik or not accession:
        return None
    cik_no_padding = str(int("".join(character for character in str(cik) if character.isdigit())))
    accession_no_dashes = str(accession).replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik_no_padding}/{accession_no_dashes}/"


def _attach_raw_structure(result_dict: dict, content: str, item_results: list, raw_section_available: bool = True) -> None:
    for item_payload, item_result in zip(result_dict.get("item_results", []), item_results):
        item_payload["raw_structure"] = _raw_structure_contract(content, item_result)
        item_payload["raw_section_available"] = raw_section_available and item_result.status == "success"


def _append_supplemental_items(result_dict: dict, raw_section_available: bool = True) -> None:
    for item_payload in list(result_dict.get("item_results", [])):
        chunk = item_payload.get("raw_structure", {}).get("supplemental_chunk")
        if not chunk:
            continue
        item_payload["raw_structure"]["supplemental_chunk"] = None
        result_dict["item_results"].append(
            _supplemental_item_payload(item_payload.get("item", ""), chunk, raw_section_available=raw_section_available)
        )


def _supplemental_item_payload(source_item: str, chunk: dict, raw_section_available: bool = True) -> dict:
    return {
        "item": f"supplemental-{source_item.lower()}",
        "display_label": f"Supplemental after Item {source_item}",
        "title": chunk["label"],
        "status": "success",
        "text": chunk.get("text", ""),
        "start_offset": None,
        "end_offset": None,
        "confidence_level": "high",
        "confidence_score": 1.0,
        "confidence_components": [],
        "start_evidence": None,
        "end_evidence": None,
        "candidate_attempts": [],
        "validation_reasons": ["SUPPLEMENTAL_CHUNK_PARTITIONED_AFTER_ITEM_16"],
        "warnings": [],
        "recommended_actions": [],
        "strategy_used": "raw_supplemental_chunk_v1",
        "raw_section_available": raw_section_available,
        "raw_structure": {
            "table_count": chunk.get("table_count", 0),
            "image_count": chunk.get("image_count", 0),
            "outline": [section["label"] for section in chunk.get("sections", [])],
            "sections": chunk.get("sections", []),
            "supplemental_chunk": None,
            "raw_bytes": chunk.get("raw_bytes", 0),
        },
    }


def _raw_structure_contract(content: str, item_result) -> dict:
    structure = raw_structure_counts(content, item_result)
    structure["outline"] = []
    structure["sections"] = []
    structure["supplemental_chunk"] = None
    structure["section_mode"] = None
    structure["raw_bytes"] = 0
    try:
        _, _, fragment = raw_section_fragment(content, item_result)
    except ValueError:
        return structure
    structure["raw_bytes"] = len(fragment.encode("utf-8", errors="replace"))
    internal_chunk = raw_fragment_internal_toc_chunk(fragment, item_result.item)
    if internal_chunk and _should_use_internal_toc_sections(item_result.item, fragment, internal_chunk):
        structure["outline"] = [section["label"] for section in internal_chunk.get("sections", [])]
        structure["sections"] = internal_chunk.get("sections", [])
        structure["section_mode"] = "internal_toc"
    else:
        structure["outline"] = raw_fragment_outline(fragment)
        structure["sections"] = raw_fragment_outline_sections(fragment)
    exhibit_links = raw_fragment_exhibit_links(fragment)
    if not structure["sections"] and item_result.text:
        structure["sections"] = _text_outline_sections(item_result.text, exhibit_links)
        structure["outline"] = [section["label"] for section in structure["sections"]]
    elif exhibit_links:
        _attach_exhibit_links(structure["sections"], exhibit_links)
    if _can_partition_supplemental(item_result.item):
        structure["supplemental_chunk"] = raw_fragment_supplemental_chunk(fragment)
    return structure


def _can_partition_supplemental(item_name: str) -> bool:
    return item_name.upper() in {"15", "16"}


def _should_use_internal_toc_sections(item_name: str, fragment: str, chunk: dict) -> bool:
    sections = chunk.get("sections", [])
    if len(sections) < 3:
        return False
    if item_name.upper() in {"8", "14", "15"}:
        return True
    raw_bytes = len(fragment.encode("utf-8", errors="replace"))
    return raw_bytes > 750000 and chunk.get("table_count", 0) >= 3


def _text_outline_sections(text: str, exhibit_links: dict[str, dict] | None = None, limit: int = 30) -> list[dict]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    starts: list[tuple[int, int, str]] = []
    seen = set()
    for index, line in enumerate(lines):
        label = ""
        content_start = index + 1
        if re.fullmatch(r"\d{1,2}", line) and index + 1 < len(lines) and _looks_like_text_outline_label(lines[index + 1]):
            label = f"{line} {lines[index + 1]}"
            content_start = index + 2
        elif re.fullmatch(r"\d+(?:\.\d+)+[A-Z]?", line) and index + 1 < len(lines):
            label = line
            content_start = index + 1
        elif not (index > 0 and re.fullmatch(r"\d{1,2}", lines[index - 1])) and _looks_like_text_outline_label(line):
            label = line
        if not label:
            continue
        label = label[:140]
        key = label.lower()
        if key in seen:
            continue
        seen.add(key)
        starts.append((index, content_start, label))
        if len(starts) >= limit:
            break

    sections = []
    for position, (heading_index, content_start, label) in enumerate(starts):
        next_heading_index = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        section_text = "\n".join(lines[content_start:next_heading_index]).strip()
        section = {
            "label": label,
            "text": section_text[:6000] + ("\n[truncated]" if len(section_text) > 6000 else ""),
            "raw_bytes": len(section_text.encode("utf-8", errors="replace")),
            "table_count": 0,
            "image_count": 0,
        }
        _attach_exhibit_link(section, exhibit_links or {})
        sections.append(section)
    return sections


def _attach_exhibit_links(sections: list[dict], exhibit_links: dict[str, dict]) -> None:
    for section in sections:
        _attach_exhibit_link(section, exhibit_links)


def _attach_exhibit_link(section: dict, exhibit_links: dict[str, dict]) -> None:
    number_match = re.match(r"(?P<number>\d+(?:\.\d+)+[A-Z]?)\b", section.get("label", ""))
    if not number_match:
        return
    link = exhibit_links.get(number_match.group("number"))
    if not link:
        return
    section["href"] = link["href"]
    if section["label"] == number_match.group("number"):
        section["label"] = f"{section['label']} {link['label']}"[:180]


def _looks_like_text_outline_label(value: str) -> bool:
    if not 8 <= len(value) <= 180:
        return False
    if value.lower().startswith("item "):
        return False
    if re.fullmatch(r"[\d.,$%() -]+", value):
        return False
    if re.search(r"\.{2,}\s*\d+\s*$", value):
        return False
    alpha_count = sum(1 for character in value if character.isalpha())
    if alpha_count < 5:
        return False
    uppercase_ratio = sum(1 for character in value if character.isupper()) / max(alpha_count, 1)
    return uppercase_ratio > 0.55 or (value[:1].isupper() and not value.endswith("."))


def _parse_multipart_form(content_type: str, body: bytes) -> tuple[dict[str, str], dict[str, dict]]:
    if "multipart/form-data" not in content_type.lower():
        raise ValueError("multipart/form-data is required")
    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + body
    )
    if not message.is_multipart():
        raise ValueError("multipart body is malformed")

    fields: dict[str, str] = {}
    files: dict[str, dict] = {}
    for part in message.iter_parts():
        if part.get_content_disposition() != "form-data":
            continue
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        data = part.get_payload(decode=True) or b""
        filename = part.get_filename()
        if filename:
            files[name] = {
                "filename": _safe_filename(filename),
                "content_type": part.get_content_type(),
                "content": data,
            }
        else:
            fields[name] = data.decode(part.get_content_charset() or "utf-8", errors="replace")
    return fields, files


class WebUiHandler(BaseHTTPRequestHandler):
    server_version = "SecItemExtractorWeb/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/":
            self._send_html(render_home())
            return
        if path.startswith("/assets/"):
            self._send_static(path.removeprefix("/assets/"))
            return
        if path == "/testing":
            self._send_html(render_testing())
            return
        if path == "/sec-live":
            query = parse_qs(parsed.query)
            self._send_html(
                render_live_detail(
                    ticker=_first_query_value(query, "ticker"),
                    fiscal_year=_first_query_value(query, "year"),
                )
            )
            return
        if path == "/upload":
            self._send_html(render_upload_detail())
            return
        if path.startswith("/filings/"):
            filing_id = unquote(path.removeprefix("/filings/"))
            self._send_html(render_detail(filing_id))
            return
        if path == "/api/filings":
            self._send_json({"filings": filing_options()})
            return
        if path == "/api/live-smoke":
            self._send_json(live_smoke_data())
            return
        if path == "/api/health":
            self._send_json(health_check())
            return
        if path == "/api/sec/intake-plan":
            query = parse_qs(parsed.query)
            self._handle_sec_intake_plan(
                ticker=_first_query_value(query, "ticker"),
                cik=_first_query_value(query, "cik"),
                fiscal_year=_first_query_value(query, "year"),
            )
            return
        if path == "/api/sec/extract":
            query = parse_qs(parsed.query)
            self._handle_sec_extract(
                ticker=_first_query_value(query, "ticker"),
                cik=_first_query_value(query, "cik"),
                fiscal_year=_first_query_value(query, "year"),
            )
            return
        if path.startswith("/api/filings/") and path.endswith("/raw-metadata"):
            filing_id = unquote(path.removeprefix("/api/filings/").removesuffix("/raw-metadata"))
            self._handle_raw_metadata(filing_id)
            return
        if path.startswith("/api/filings/") and path.endswith("/extract"):
            filing_id = unquote(path.removeprefix("/api/filings/").removesuffix("/extract"))
            self._handle_extract(filing_id)
            return
        if path.startswith("/api/filings/") and "/raw-section/" in path:
            filing_id, item = unquote(path.removeprefix("/api/filings/")).split("/raw-section/", 1)
            self._handle_raw_section(filing_id, item)
            return

        self._send_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if path == "/api/uploads/identify":
            self._handle_upload_identify()
            return
        if path == "/api/uploads/extract":
            self._handle_upload_extract()
            return
        if path.startswith("/api/filings/") and path.endswith("/recover"):
            filing_id = unquote(path.removeprefix("/api/filings/").removesuffix("/recover"))
            self._handle_recover(filing_id)
            return
        self._send_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        return

    def _handle_raw_metadata(self, filing_id: str) -> None:
        try:
            self._send_json(raw_filing_metadata(filing_id))
        except KeyError:
            self._send_json({"error": "unknown_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)
        except FileNotFoundError:
            self._send_json({"error": "missing_raw_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)

    def _handle_sec_intake_plan(self, ticker: str, cik: str, fiscal_year: str) -> None:
        try:
            payload = sec_intake_plan(ticker=ticker, cik=cik, fiscal_year=fiscal_year)
            status = HTTPStatus.OK if payload["status"] != "blocked" else HTTPStatus.PRECONDITION_REQUIRED
            self._send_json(payload, status=status)
        except ValueError as error:
            self._send_json({"error": "bad_sec_query", "message": str(error)}, status=HTTPStatus.BAD_REQUEST)

    def _handle_sec_extract(self, ticker: str, cik: str, fiscal_year: str) -> None:
        try:
            payload = extract_sec_filing(ticker=ticker, cik=cik, fiscal_year=fiscal_year)
            if payload["status"] == "blocked":
                status = HTTPStatus.PRECONDITION_REQUIRED
            elif payload["status"] == "not_found":
                status = HTTPStatus.NOT_FOUND
            else:
                status = HTTPStatus.OK
            self._send_json(payload, status=status)
        except ValueError as error:
            self._send_json({"error": "bad_sec_query", "message": str(error)}, status=HTTPStatus.BAD_REQUEST)

    def _handle_upload_identify(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            self._send_json({"error": "bad_upload", "message": "invalid content length"}, status=HTTPStatus.BAD_REQUEST)
            return
        if content_length <= 0:
            self._send_json({"error": "bad_upload", "message": "uploaded filing file is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        if content_length > MAX_UPLOAD_BYTES + 20000:
            self._send_json(
                {"error": "upload_too_large", "message": f"upload identification exceeds {MAX_UPLOAD_BYTES} byte limit"},
                status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            )
            return

        body = self.rfile.read(content_length)
        try:
            fields, files = _parse_multipart_form(self.headers.get("Content-Type", ""), body)
            upload = files.get("filing") or files.get("file")
            if upload is None:
                raise ValueError("file field named filing is required")
            original_size = _parse_optional_int(fields.get("original_size"))
            payload = identify_uploaded_filing(
                upload["content"],
                upload["filename"],
                original_size=original_size,
                partial_upload=fields.get("partial_upload") == "1",
            )
            self._send_json(payload)
        except ValueError as error:
            self._send_json({"error": "bad_upload", "message": str(error)}, status=HTTPStatus.BAD_REQUEST)

    def _handle_upload_extract(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            self._send_json({"error": "bad_upload", "message": "invalid content length"}, status=HTTPStatus.BAD_REQUEST)
            return
        if content_length <= 0:
            self._send_json({"error": "bad_upload", "message": "uploaded filing file is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        if content_length > MAX_UPLOAD_BYTES + 20000:
            self._send_json(
                {"error": "upload_too_large", "message": f"upload exceeds {MAX_UPLOAD_BYTES} byte limit"},
                status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            )
            return

        body = self.rfile.read(content_length)
        try:
            fields, files = _parse_multipart_form(self.headers.get("Content-Type", ""), body)
            upload = files.get("filing") or files.get("file")
            if upload is None:
                raise ValueError("file field named filing is required")
            payload = extract_uploaded_filing(
                upload["content"],
                upload["filename"],
            )
            self._send_json(payload)
        except ValueError as error:
            self._send_json({"error": "bad_upload", "message": str(error)}, status=HTTPStatus.BAD_REQUEST)

    def _handle_extract(self, filing_id: str) -> None:
        try:
            self._send_json(extract_seed_filing(filing_id))
        except KeyError:
            self._send_json({"error": "unknown_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)
        except FileNotFoundError:
            self._send_json({"error": "missing_raw_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)

    def _handle_raw_section(self, filing_id: str, item: str) -> None:
        try:
            self._send_json(raw_section_preview(filing_id, item))
        except KeyError:
            self._send_json({"error": "unknown_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)
        except FileNotFoundError:
            self._send_json({"error": "missing_raw_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)
        except ValueError as error:
            self._send_json({"error": "raw_section_unavailable", "message": str(error)}, status=HTTPStatus.NOT_FOUND)

    def _handle_recover(self, filing_id: str) -> None:
        try:
            payload = self._read_json_body()
            selections = _parse_recovery_selections(payload, filing_id)
            self._send_json(recover_seed_filing(filing_id, selections=selections))
        except json.JSONDecodeError:
            self._send_json({"error": "bad_json"}, status=HTTPStatus.BAD_REQUEST)
        except KeyError:
            self._send_json({"error": "unknown_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)
        except FileNotFoundError:
            self._send_json({"error": "missing_raw_filing", "filing_id": filing_id}, status=HTTPStatus.NOT_FOUND)

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length)
        payload = json.loads(body.decode("utf-8"))
        return payload if isinstance(payload, dict) else {}

    def _send_html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self._send_no_cache_headers("text/html; charset=utf-8", len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_no_cache_headers("application/json; charset=utf-8", len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_static(self, asset_name: str) -> None:
        safe_name = Path(asset_name).name
        path = FRONTEND_DIR / safe_name
        if not path.exists() or not path.is_file():
            self._send_json({"error": "asset_not_found"}, status=HTTPStatus.NOT_FOUND)
            return
        encoded = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self._send_no_cache_headers(content_type, len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_no_cache_headers(self, content_type: str, content_length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_length))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")


def _first_query_value(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key, [])
    return values[0] if values else ""


def _parse_optional_int(value: str | None) -> int | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        parsed = int(str(value).strip())
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def health_check() -> dict:
    return {
        "status": "ok",
        "service": "sec-item-extractor",
        "parser_version": "0.1.0",
        "live_sec_enabled": bool(os.environ.get("SEC_USER_AGENT", "").strip()),
    }


def render_home() -> str:
    return _react_page("SEC 10-K Item Extractor")
    year_options = _sec_year_options(default_year=2023)
    body = """
        <main class="home-shell">
          <section class="selector-panel">
            <div class="toolbar">
              <div>
                <h1>SEC 10-K Test Filings</h1>
                <p class="muted">Choose a local seed filing. Extraction runs only after you open a filing.</p>
              </div>
              <div class="toolbar-actions">
                <a class="secondary-button compact" href="/upload">Upload filing</a>
                <button id="refresh-filings" class="icon-button" title="Refresh filing list" aria-label="Refresh filing list">R</button>
              </div>
            </div>
            <form id="sec-intake-form" class="sec-intake-panel">
              <div>
                <h2>Live SEC intake</h2>
                <p class="muted">Resolve ticker/year metadata without caching raw filings by default.</p>
              </div>
              <label>Ticker<input name="ticker" value="AAPL" autocomplete="off"></label>
              <label>Fiscal year<select name="year">__YEAR_OPTIONS__</select></label>
              <div class="sec-intake-buttons">
                <button class="secondary-button compact" type="submit" data-sec-mode="plan">Check SEC filing</button>
                <button class="secondary-button compact" type="submit" data-sec-mode="extract">Run live extraction</button>
              </div>
              <pre id="sec-intake-result"></pre>
            </form>
            <section id="live-smoke-data" class="live-smoke-panel">
              <div>
                <h2>Live smoke raw data</h2>
                <p class="muted">Latest SEC direct-fetch smoke run, loaded from reports.</p>
              </div>
              <div id="live-smoke-summary" class="live-smoke-summary"></div>
              <details>
                <summary>Raw JSON</summary>
                <pre id="live-smoke-json"></pre>
              </details>
            </section>
            <div id="filing-list" class="filing-grid" aria-live="polite"></div>
          </section>
        </main>
        <script>
        const list = document.getElementById("filing-list");
        const secIntakeForm = document.getElementById("sec-intake-form");
        const secIntakeResult = document.getElementById("sec-intake-result");
        const liveSmokeSummary = document.getElementById("live-smoke-summary");
        const liveSmokeJson = document.getElementById("live-smoke-json");
        document.getElementById("refresh-filings").addEventListener("click", loadFilings);
        let secIntakeMode = 'plan';
        for (const button of secIntakeForm.querySelectorAll('[data-sec-mode]')) {
          button.addEventListener('click', () => { secIntakeMode = button.dataset.secMode; });
        }
        secIntakeForm.addEventListener("submit", checkSecIntake);
        loadFilings();
        loadLiveSmokeData();

        async function loadFilings() {
          list.innerHTML = '<div class="loading">Loading filings...</div>';
          const response = await fetch('/api/filings', {cache: 'no-store'});
          const payload = await response.json();
          list.innerHTML = '';
          for (const filing of payload.filings) {
            const link = document.createElement('a');
            link.className = 'filing-card';
            link.href = `/filings/${encodeURIComponent(filing.filing_id)}`;
            link.innerHTML = `
              <span class="ticker">${escapeHtml(filing.ticker)}</span>
              <span class="meta">${escapeHtml(filing.industry)} | ${filing.fiscal_year} | ${escapeHtml(filing.form)}</span>
              <span class="${filing.available ? 'available' : 'missing'}">${filing.available ? 'available' : 'missing raw filing'}</span>
            `;
            list.appendChild(link);
          }
        }

        async function checkSecIntake(event) {
          event.preventDefault();
          const params = new URLSearchParams(new FormData(secIntakeForm));
          if (secIntakeMode === 'extract') {
            window.location.href = `/sec-live?${params.toString()}`;
            return;
          }
          const endpoint = secIntakeMode === 'extract' ? '/api/sec/extract' : '/api/sec/intake-plan';
          secIntakeResult.textContent = secIntakeMode === 'extract'
            ? 'Fetching SEC filing and running extraction...'
            : 'Resolving SEC metadata...';
          const response = await fetch(`${endpoint}?${params.toString()}`, {cache: 'no-store'});
          const payload = await response.json();
          secIntakeResult.textContent = secIntakeMode === 'extract'
            ? JSON.stringify(liveExtractionSummary(payload), null, 2)
            : JSON.stringify(payload, null, 2);
        }

        function liveExtractionSummary(payload) {
          if (payload.status !== 'success') return payload;
          return {
            status: payload.status,
            message: payload.message,
            filing: payload.filing,
            source_bytes: payload.source_bytes,
            elapsed_ms: payload.elapsed_ms,
            storage_policy: payload.storage_policy,
            summary: payload.summary,
            first_items: (payload.result?.item_results || []).slice(0, 8).map(item => ({
              item: item.item,
              status: item.status,
              confidence: item.confidence_level,
              text_length: (item.text || '').length,
              warnings: item.warnings || [],
              actions: (item.recommended_actions || []).length,
            })),
          };
        }

        async function loadLiveSmokeData() {
          liveSmokeSummary.innerHTML = '<div class="loading slim">Loading live smoke report...</div>';
          const response = await fetch('/api/live-smoke', {cache: 'no-store'});
          const payload = await response.json();
          liveSmokeJson.textContent = JSON.stringify(payload, null, 2);
          if (!payload.available) {
            liveSmokeSummary.innerHTML = '<p class="muted">No live smoke report has been generated yet.</p>';
            return;
          }
          const summary = payload.summary || {};
          const filings = payload.filings || [];
          liveSmokeSummary.innerHTML = `
            <div class="metadata-row">
              <span>${escapeHtml(summary.filings_tested)} filings</span>
              <span>${escapeHtml(summary.warning_total)} warnings</span>
              <span>${escapeHtml(summary.failed_total)} failed</span>
              <span>${escapeHtml(summary.recommended_action_total)} actions</span>
            </div>
            <div class="live-smoke-table">
              ${filings.map(filing => `
                <a href="/sec-live?ticker=${encodeURIComponent(filing.ticker)}&year=${encodeURIComponent(filing.year)}">
                  <strong>${escapeHtml(filing.ticker)} ${escapeHtml(filing.year)}</strong>
                  <span>${escapeHtml(filing.filing_status)} | warnings ${escapeHtml(filing.warning_count)} | actions ${escapeHtml(filing.recommended_action_count)}</span>
                </a>
              `).join('')}
            </div>
          `;
        }
        </script>
        """.replace("__YEAR_OPTIONS__", year_options)
    return _page("SEC 10-K Filing Selector", body)


def _sec_year_options(default_year: int) -> str:
    current_year = time.localtime().tm_year
    return "".join(
        f'<option value="{year}"{" selected" if year == default_year else ""}>{year}</option>'
        for year in range(current_year, 1993, -1)
    )


def render_testing() -> str:
    return _react_page("SEC 10-K Testing")


def render_upload_detail() -> str:
    return _react_page("Upload SEC Filing")
    return _page(
        "Upload SEC Filing",
        """
        <main class="workspace-shell">
          <aside class="toc-panel">
            <a class="back-link" href="/">Back to filings</a>
            <h1 id="filing-title">Upload filing</h1>
            <p id="run-meta" class="muted">Upload HTML/TXT and extract in memory.</p>
            <form id="upload-form" class="upload-form">
              <label>Filing file<input name="filing" type="file" accept=".html,.htm,.txt,text/html,text/plain" required></label>
              <button class="primary-button" type="submit">Run upload extraction</button>
            </form>
            <h2 class="toc-heading">Extracted TOC</h2>
            <nav id="toc-list" class="toc-list" aria-label="Uploaded item navigation"></nav>
          </aside>
          <section class="item-panel">
            <div id="status-banner" class="status-banner">Choose a filing file to parse.</div>
            <section id="metadata-panel" class="metadata-panel"></section>
            <div id="items" class="items"></div>
            <section class="live-raw-panel">
              <details>
                <summary>Upload extraction raw data</summary>
                <pre id="upload-raw-json"></pre>
              </details>
            </section>
          </section>
        </main>
        <script>
        const uploadForm = document.getElementById('upload-form');
        const tocList = document.getElementById('toc-list');
        const items = document.getElementById('items');
        const statusBanner = document.getElementById('status-banner');
        const runMeta = document.getElementById('run-meta');
        const metadataPanel = document.getElementById('metadata-panel');
        const uploadRawJson = document.getElementById('upload-raw-json');

        uploadForm.addEventListener('submit', runUploadExtraction);

        async function runUploadExtraction(event) {
          event.preventDefault();
          const formData = new FormData(uploadForm);
          statusBanner.textContent = 'Uploading filing and running extraction...';
          statusBanner.classList.remove('error');
          tocList.innerHTML = '';
          metadataPanel.innerHTML = '';
          items.innerHTML = '<div class="loading">Parsing uploaded filing and reconstructing item boundaries...</div>';
          uploadRawJson.textContent = '';
          try {
            const response = await fetch('/api/uploads/extract', {
              method: 'POST',
              cache: 'no-store',
              body: formData,
            });
            const payload = await response.json();
            uploadRawJson.textContent = JSON.stringify(payload, null, 2);
            if (!response.ok) throw new Error(payload.message || payload.error || 'upload_extract_failed');
            renderUploadExtraction(payload);
          } catch (error) {
            statusBanner.textContent = `Upload extraction failed: ${error.message}`;
            statusBanner.classList.add('error');
            items.innerHTML = '';
          }
        }

        function renderUploadExtraction(payload) {
          const result = payload.result || {item_results: []};
          const metadata = payload.inferred_metadata || {};
          document.getElementById('filing-title').textContent = `${payload.filing.ticker || 'Unknown'} ${payload.filing.fiscal_year || ''}`.trim();
          runMeta.textContent = `${payload.filing.form || 'Unknown form'} | ${payload.filing.primary_document} | ${Number(payload.source_bytes || 0).toLocaleString()} bytes | ${payload.elapsed_ms} ms`;
          statusBanner.textContent = `${payload.summary.status} | ${payload.summary.item_count} items | TOC ${payload.summary.toc_confidence} | warnings ${payload.summary.warning_count}`;
          metadataPanel.innerHTML = `
            <div class="metadata-row">
              <span>${escapeHtml(payload.filing.primary_document)}</span>
              <span>Ticker ${escapeHtml(payload.filing.ticker || 'unknown')} (${escapeHtml(metadata.ticker_source || 'not_found')})</span>
              <span>Fiscal year ${escapeHtml(payload.filing.fiscal_year || 'unknown')} (${escapeHtml(metadata.fiscal_year_source || 'not_found')})</span>
              <span>Form ${escapeHtml(payload.filing.form || 'unknown')} (${escapeHtml(metadata.form_source || 'not_found')})</span>
              <span>Registrant ${escapeHtml(metadata.registrant_name || 'unknown')}</span>
              <span>${escapeHtml(payload.source_sha256.slice(0, 12))}</span>
              <span>${escapeHtml(payload.message)}</span>
            </div>
          `;
          renderUploadToc(result);
          renderUploadItems(result.item_results || []);
        }

        function renderUploadToc(result) {
          const titles = new Map((result.toc_entries || []).map(entry => [entry.item, entry.title || entry.text]));
          tocList.innerHTML = '';
          for (const item of result.item_results || []) {
            const link = document.createElement('a');
            link.href = `#item-${cssId(item.item)}`;
            link.className = `toc-link ${item.status} ${item.confidence_level}`;
            const label = item.display_label || `Item ${item.item}`;
            link.innerHTML = `
              <span>${escapeHtml(label)}</span>
              <small>${escapeHtml(item.title || titles.get(item.item) || item.status)}</small>
              <em>${escapeHtml(item.status)} | ${escapeHtml(item.confidence_level)} ${Number(item.confidence_score).toFixed(2)}</em>
            `;
            tocList.appendChild(link);
          }
        }

        function renderUploadItems(itemResults) {
          items.innerHTML = '';
          for (const item of itemResults) {
            const article = document.createElement('article');
            article.className = 'item-card';
            article.id = `item-${cssId(item.item)}`;
            const warnings = (item.warnings || []).length
              ? item.warnings.map(warning => `<span class="warning-chip">${escapeHtml(warning)}</span>`).join('')
              : '<span class="empty-chip">none</span>';
            const actions = (item.recommended_actions || []).length
              ? item.recommended_actions.map(action => `<span class="action-chip ${escapeHtml(action.severity)}">${escapeHtml(action.action_type)}:${escapeHtml(action.reason)}</span>`).join('')
              : '<span class="empty-chip">none</span>';
            const rawStructure = item.raw_structure || {};
            const tableCount = Number(rawStructure.table_count || 0);
            const imageCount = Number(rawStructure.image_count || 0);
            const structureTags = [
              tableCount ? `<span class="structure-tag table">tables ${tableCount}</span>` : '',
              imageCount ? `<span class="structure-tag image">images ${imageCount}</span>` : '',
            ].join('');
            const rawTools = item.live_raw_section_available ? `
              <div class="raw-section-tools">
                <button class="secondary-button compact" data-upload-raw-item="${escapeHtml(item.item)}">Show original filing structure</button>
                <span class="raw-section-meta"></span>
              </div>
              <div class="raw-section-preview"></div>
            ` : '';
            article.innerHTML = `
              <header class="item-header">
                <div>
                  <h2>${escapeHtml(item.display_label || `Item ${item.item}`)}</h2>
                  <p class="muted">${escapeHtml(item.status)} | ${escapeHtml(item.confidence_level)} ${Number(item.confidence_score).toFixed(2)} | ${(item.text || '').length.toLocaleString()} chars</p>
                </div>
                <div class="item-badges">
                  ${structureTags}
                  <span class="pill ${escapeHtml(item.confidence_level)}">${escapeHtml(item.confidence_level)}</span>
                </div>
              </header>
              <div class="extracted-view">
                <dl class="evidence-grid">
                  <div><dt>Start</dt><dd>${escapeHtml(item.start_evidence?.text || 'none')}</dd></div>
                  <div><dt>End</dt><dd>${escapeHtml(item.end_evidence?.text || 'none')}</dd></div>
                  <div><dt>Warnings</dt><dd class="chip-row">${warnings}</dd></div>
                  <div><dt>Actions</dt><dd class="chip-row">${actions}</dd></div>
                </dl>
                <pre class="item-text"></pre>
              </div>
              ${rawTools}
            `;
            article.querySelector('.item-text').textContent = item.text || '';
            const rawButton = article.querySelector('[data-upload-raw-item]');
            if (rawButton) rawButton.addEventListener('click', () => toggleUploadRawSection(item, article, rawButton));
            items.appendChild(article);
          }
        }

        function toggleUploadRawSection(item, container, button) {
          const toolRow = button.closest('.raw-section-tools');
          const meta = toolRow.querySelector('.raw-section-meta');
          const preview = toolRow.nextElementSibling;
          const extractedView = container.querySelector('.extracted-view');
          if (container.dataset.rawVisible === 'true') {
            container.dataset.rawVisible = 'false';
            extractedView.hidden = false;
            preview.hidden = true;
            button.textContent = 'Show original filing structure';
            meta.textContent = '';
            return;
          }
          const raw = item.live_raw_section || {};
          container.dataset.rawVisible = 'true';
          extractedView.hidden = true;
          preview.hidden = false;
          button.textContent = 'Show extracted view';
          meta.textContent = `${Number(raw.table_count || 0)} tables | ${Number(raw.image_count || 0)} images | ${Number(raw.raw_bytes || 0).toLocaleString()} bytes`;
          if (preview.dataset.loaded === 'true') return;
          const iframe = document.createElement('iframe');
          iframe.className = 'raw-section-frame';
          iframe.setAttribute('sandbox', '');
          iframe.srcdoc = raw.srcdoc || '<!doctype html><p>Original section unavailable.</p>';
          preview.appendChild(iframe);
          preview.dataset.loaded = 'true';
        }
        </script>
        """,
    )


def render_live_detail(ticker: str, fiscal_year: str) -> str:
    return _react_page(f"{(ticker or '').strip().upper()} {fiscal_year} Live SEC Extraction")
    safe_ticker = json.dumps((ticker or "").strip().upper())
    safe_year = json.dumps((fiscal_year or "").strip())
    template = """
        <main class="workspace-shell">
          <aside class="toc-panel">
            <a class="back-link" href="/">Back to filings</a>
            <h1 id="filing-title">Live SEC filing</h1>
            <p id="run-meta" class="muted">Direct SEC fetch, no raw persistence.</p>
            <h2 class="toc-heading">Extracted TOC</h2>
            <nav id="toc-list" class="toc-list" aria-label="Extracted item navigation"></nav>
          </aside>
          <section class="item-panel">
            <div id="status-banner" class="status-banner">Fetching SEC filing and running extraction...</div>
            <section id="metadata-panel" class="metadata-panel"></section>
            <div id="items" class="items"></div>
            <section class="live-raw-panel">
              <details open>
                <summary>Raw extraction JSON</summary>
                <pre id="live-raw-json"></pre>
              </details>
            </section>
          </section>
        </main>
        <script>
        const liveTicker = __LIVE_TICKER__;
        const liveYear = __LIVE_YEAR__;
        const tocList = document.getElementById('toc-list');
        const items = document.getElementById('items');
        const statusBanner = document.getElementById('status-banner');
        const runMeta = document.getElementById('run-meta');
        const metadataPanel = document.getElementById('metadata-panel');
        const liveRawJson = document.getElementById('live-raw-json');

        runLiveExtraction();

        async function runLiveExtraction() {
          const params = new URLSearchParams({ticker: liveTicker, year: liveYear});
          items.innerHTML = '<div class="loading">Fetching SEC filing and reconstructing item boundaries...</div>';
          try {
            const response = await fetch(`/api/sec/extract?${params.toString()}`, {cache: 'no-store'});
            const payload = await response.json();
            liveRawJson.textContent = JSON.stringify(payload, null, 2);
            if (!response.ok) throw new Error(payload.message || payload.error || 'live_extract_failed');
            renderLiveExtraction(payload);
          } catch (error) {
            statusBanner.textContent = `Live extraction failed: ${error.message}`;
            statusBanner.classList.add('error');
            items.innerHTML = '';
          }
        }

        function renderLiveExtraction(payload) {
          const result = payload.result || {item_results: []};
          document.getElementById('filing-title').textContent = `${payload.filing.ticker} ${payload.filing.fiscal_year}`;
          runMeta.textContent = `${payload.filing.form} | ${payload.filing.accession_number} | ${Number(payload.source_bytes || 0).toLocaleString()} bytes | ${payload.elapsed_ms} ms`;
          statusBanner.textContent = `${payload.summary.status} | ${payload.summary.item_count} items | TOC ${payload.summary.toc_confidence} | warnings ${payload.summary.warning_count}`;
          metadataPanel.innerHTML = `
            <div class="metadata-row">
              <span>${escapeHtml(payload.filing.title || payload.filing.ticker)}</span>
              <span>CIK ${escapeHtml(payload.filing.cik)}</span>
              <span>report ${escapeHtml(payload.filing.report_date)}</span>
              <a href="${escapeHtml(payload.filing.download_url)}" target="_blank" rel="noopener noreferrer">SEC source</a>
            </div>
          `;
          renderLiveToc(result);
          renderLiveItems(result.item_results || []);
        }

        function renderLiveToc(result) {
          const titles = new Map((result.toc_entries || []).map(entry => [entry.item, entry.title || entry.text]));
          tocList.innerHTML = '';
          for (const item of result.item_results || []) {
            const link = document.createElement('a');
            link.href = `#item-${cssId(item.item)}`;
            link.className = `toc-link ${item.status} ${item.confidence_level}`;
            const label = item.display_label || `Item ${item.item}`;
            link.innerHTML = `
              <span>${escapeHtml(label)}</span>
              <small>${escapeHtml(item.title || titles.get(item.item) || item.status)}</small>
              <em>${escapeHtml(item.status)} | ${escapeHtml(item.confidence_level)} ${Number(item.confidence_score).toFixed(2)}</em>
            `;
            tocList.appendChild(link);
          }
        }

        function renderLiveItems(itemResults) {
          items.innerHTML = '';
          for (const item of itemResults) {
            const article = document.createElement('article');
            article.className = 'item-card';
            article.id = `item-${cssId(item.item)}`;
            const warnings = (item.warnings || []).length
              ? item.warnings.map(warning => `<span class="warning-chip">${escapeHtml(warning)}</span>`).join('')
              : '<span class="empty-chip">none</span>';
            const actions = (item.recommended_actions || []).length
              ? item.recommended_actions.map(action => `<span class="action-chip ${escapeHtml(action.severity)}">${escapeHtml(action.action_type)}:${escapeHtml(action.reason)}</span>`).join('')
              : '<span class="empty-chip">none</span>';
            const rawStructure = item.raw_structure || {};
            const tableCount = Number(rawStructure.table_count || 0);
            const imageCount = Number(rawStructure.image_count || 0);
            const structureTags = [
              tableCount ? `<span class="structure-tag table">tables ${tableCount}</span>` : '',
              imageCount ? `<span class="structure-tag image">images ${imageCount}</span>` : '',
            ].join('');
            const rawTools = item.live_raw_section_available ? `
              <div class="raw-section-tools">
                <button class="secondary-button compact" data-live-raw-item="${escapeHtml(item.item)}">Show original filing structure</button>
                <span class="raw-section-meta"></span>
              </div>
              <div class="raw-section-preview"></div>
            ` : '';
            article.innerHTML = `
              <header class="item-header">
                <div>
                  <h2>${escapeHtml(item.display_label || `Item ${item.item}`)}</h2>
                  <p class="muted">${escapeHtml(item.status)} | ${escapeHtml(item.confidence_level)} ${Number(item.confidence_score).toFixed(2)} | ${(item.text || '').length.toLocaleString()} chars</p>
                </div>
                <div class="item-badges">
                  ${structureTags}
                  <span class="pill ${escapeHtml(item.confidence_level)}">${escapeHtml(item.confidence_level)}</span>
                </div>
              </header>
              <div class="extracted-view">
                <dl class="evidence-grid">
                  <div><dt>Start</dt><dd>${escapeHtml(item.start_evidence?.text || 'none')}</dd></div>
                  <div><dt>End</dt><dd>${escapeHtml(item.end_evidence?.text || 'none')}</dd></div>
                  <div><dt>Warnings</dt><dd class="chip-row">${warnings}</dd></div>
                  <div><dt>Actions</dt><dd class="chip-row">${actions}</dd></div>
                </dl>
                <pre class="item-text"></pre>
              </div>
              ${rawTools}
            `;
            article.querySelector('.item-text').textContent = item.text || '';
            const rawButton = article.querySelector('[data-live-raw-item]');
            if (rawButton) rawButton.addEventListener('click', () => toggleLiveRawSection(item, article, rawButton));
            items.appendChild(article);
          }
        }

        function toggleLiveRawSection(item, container, button) {
          const toolRow = button.closest('.raw-section-tools');
          const meta = toolRow.querySelector('.raw-section-meta');
          const preview = toolRow.nextElementSibling;
          const extractedView = container.querySelector('.extracted-view');
          if (container.dataset.rawVisible === 'true') {
            container.dataset.rawVisible = 'false';
            extractedView.hidden = false;
            preview.hidden = true;
            button.textContent = 'Show original filing structure';
            meta.textContent = '';
            return;
          }
          const raw = item.live_raw_section || {};
          container.dataset.rawVisible = 'true';
          extractedView.hidden = true;
          preview.hidden = false;
          button.textContent = 'Show extracted view';
          meta.textContent = `${Number(raw.table_count || 0)} tables | ${Number(raw.image_count || 0)} images | ${Number(raw.raw_bytes || 0).toLocaleString()} bytes`;
          if (preview.dataset.loaded === 'true') return;
          const iframe = document.createElement('iframe');
          iframe.className = 'raw-section-frame';
          iframe.setAttribute('sandbox', '');
          iframe.srcdoc = raw.srcdoc || '<!doctype html><p>Original section unavailable.</p>';
          preview.appendChild(iframe);
          preview.dataset.loaded = 'true';
        }
        </script>
        """
    body = template.replace("__LIVE_TICKER__", safe_ticker).replace("__LIVE_YEAR__", safe_year)
    title = f"{(ticker or '').strip().upper()} {fiscal_year} Live SEC Extraction"
    return _page(title, body)


def render_detail(filing_id: str) -> str:
    return _react_page(f"{filing_id} Extraction")
    safe_filing_id = json.dumps(filing_id)
    return _page(
        f"{filing_id} Extraction",
        f"""
        <main class="workspace-shell">
          <aside class="toc-panel">
            <a class="back-link" href="/">Back to filings</a>
            <h1 id="filing-title">{filing_id}</h1>
            <p id="run-meta" class="muted">Pipeline has not run yet.</p>
            <div class="sidebar-actions">
              <button id="run-button" class="primary-button">Run extraction</button>
              <button id="recover-button" class="secondary-button" disabled>Run recovery actions</button>
            </div>
            <nav id="toc-list" class="toc-list" aria-label="Extracted item navigation"></nav>
          </aside>
          <section class="item-panel">
            <div id="status-banner" class="status-banner">Select Run extraction to parse this filing now.</div>
            <section id="metadata-panel" class="metadata-panel"></section>
            <div id="items" class="items"></div>
            <section id="recovery-panel" class="recovery-panel"></section>
          </section>
        </main>
        <script>
        const filingId = {safe_filing_id};
        const runButton = document.getElementById('run-button');
        const recoverButton = document.getElementById('recover-button');
        const tocList = document.getElementById('toc-list');
        const items = document.getElementById('items');
        const statusBanner = document.getElementById('status-banner');
        const runMeta = document.getElementById('run-meta');
        const metadataPanel = document.getElementById('metadata-panel');
        const recoveryPanel = document.getElementById('recovery-panel');
        let lastExtraction = null;

        runButton.addEventListener('click', runExtraction);
        recoverButton.addEventListener('click', runRecovery);
        loadMetadata();

        async function loadMetadata() {{
          metadataPanel.innerHTML = '<div class="loading slim">Loading raw filing metadata...</div>';
          const response = await fetch(`/api/filings/${{encodeURIComponent(filingId)}}/raw-metadata`, {{cache: 'no-store'}});
          const payload = await response.json();
          if (!response.ok) {{
            metadataPanel.innerHTML = `<div class="status-banner error">Metadata failed: ${{escapeHtml(payload.error || 'unknown')}}</div>`;
            return;
          }}
          metadataPanel.innerHTML = `
            <div class="metadata-row">
              <span>${{escapeHtml(payload.raw.path)}}</span>
              <span>${{Number(payload.raw.bytes).toLocaleString()}} bytes</span>
              <span>sha256 ${{escapeHtml(payload.raw.sha256.slice(0, 12))}}</span>
            </div>
          `;
        }}

        async function runExtraction() {{
          runButton.disabled = true;
          recoverButton.disabled = true;
          statusBanner.textContent = 'Running extraction pipeline...';
          tocList.innerHTML = '';
          recoveryPanel.innerHTML = '';
          items.innerHTML = '<div class="loading">Parsing filing and reconstructing item boundaries...</div>';
          try {{
            const response = await fetch(`/api/filings/${{encodeURIComponent(filingId)}}/extract`, {{cache: 'no-store'}});
            const payload = await response.json();
            if (!response.ok) throw new Error(payload.error || 'extract_failed');
            lastExtraction = payload;
            renderExtraction(payload);
          }} catch (error) {{
            statusBanner.textContent = `Extraction failed: ${{error.message}}`;
            items.innerHTML = '';
          }} finally {{
            runButton.disabled = false;
          }}
        }}

        function renderExtraction(payload) {{
          const result = payload.result;
          document.getElementById('filing-title').textContent = `${{payload.filing.ticker}} ${{payload.filing.fiscal_year}}`;
          runMeta.textContent = `${{payload.filing.industry}} | ${{payload.filing.form}} | ${{payload.source_bytes.toLocaleString()}} bytes | ${{payload.elapsed_ms}} ms`;
          statusBanner.textContent = `${{result.status}} | ${{result.item_results.length}} items | TOC ${{result.toc_confidence}}`;
          recoverButton.disabled = !result.item_results.some(item => item.recommended_actions.length);
          renderToc(result);
          renderItems(result.item_results);
          renderRecoveryControls(result.item_results);
        }}

        function renderToc(result) {{
          const titles = new Map((result.toc_entries || []).map(entry => [entry.item, entry.title || entry.text]));
          tocList.innerHTML = '';
          for (const item of result.item_results) {{
            const link = document.createElement('a');
            link.href = `#item-${{cssId(item.item)}}`;
            link.className = `toc-link ${{item.status}} ${{item.confidence_level}}`;
            const label = item.display_label || `Item ${{item.item}}`;
            link.innerHTML = `
              <span>${{escapeHtml(label)}}</span>
              <small>${{escapeHtml(item.title || titles.get(item.item) || item.status)}}</small>
              <em>${{escapeHtml(item.status)}} | ${{escapeHtml(item.confidence_level)}} ${{Number(item.confidence_score).toFixed(2)}}</em>
            `;
            tocList.appendChild(link);
          }}
        }}

        function renderItems(itemResults) {{
          items.innerHTML = '';
          for (const item of itemResults) {{
            const article = document.createElement('article');
            article.className = 'item-card';
            article.id = `item-${{cssId(item.item)}}`;
            const evidenceId = `evidence-${{cssId(item.item)}}`;
            const warningLinks = item.warnings.length
              ? item.warnings.map(warning => `<a href="#${{evidenceId}}" class="warning-chip">${{escapeHtml(warning)}}</a>`).join('')
              : '<span class="empty-chip">none</span>';
            const actionLinks = item.recommended_actions.length
              ? item.recommended_actions.map(action => `<a href="#recovery-panel" class="action-chip ${{escapeHtml(action.severity)}}">${{escapeHtml(action.action_type)}}:${{escapeHtml(action.reason)}}</a>`).join('')
              : '<span class="empty-chip">none</span>';
            const text = item.text || '';
            const isSupplemental = String(item.item || '').startsWith('supplemental-');
            const structureTags = renderStructureTags(item.raw_structure || {{}});
            const rawSections = Array.isArray(item.raw_structure?.sections) ? item.raw_structure.sections : [];
            const hasInternalTocSections = item.raw_structure?.section_mode === 'internal_toc';
            const structurePanel = (isSupplemental || hasInternalTocSections) ? renderStructurePanel(item) : '';
            const showMainText = !((isSupplemental || hasInternalTocSections) && rawSections.length);
            const rawTools = item.raw_section_available === false ? '' : `
              <div class="raw-section-tools">
                <button class="secondary-button compact" data-raw-item="${{escapeHtml(item.item)}}">Show original filing structure</button>
                <span class="raw-section-meta"></span>
              </div>
              <div class="raw-section-preview"></div>
            `;
            const heading = item.display_label || `Item ${{item.item}}`;
            article.innerHTML = `
              <header class="item-header">
                <div>
                  <h2>${{escapeHtml(heading)}}</h2>
                  <p class="muted">${{escapeHtml(item.status)}} | ${{escapeHtml(item.confidence_level)}} ${{Number(item.confidence_score).toFixed(2)}} | ${{(item.text || '').length.toLocaleString()}} chars</p>
                </div>
                <div class="item-badges">
                  ${{structureTags}}
                  <span class="pill ${{escapeHtml(item.confidence_level)}}">${{escapeHtml(item.confidence_level)}}</span>
                </div>
              </header>
              <div class="extracted-view">
                <dl id="${{evidenceId}}" class="evidence-grid">
                  <div><dt>Start</dt><dd>${{escapeHtml(item.start_evidence?.text || 'none')}}</dd></div>
                  <div><dt>End</dt><dd>${{escapeHtml(item.end_evidence?.text || 'none')}}</dd></div>
                  <div><dt>Warnings</dt><dd class="chip-row">${{warningLinks}}</dd></div>
                  <div><dt>Actions</dt><dd class="chip-row">${{actionLinks}}</dd></div>
                </dl>
                ${{structurePanel}}
                ${{showMainText ? '<pre class="item-text"></pre>' : ''}}
              </div>
              ${{rawTools}}
            `;
            const itemText = article.querySelector('.item-text');
            if (itemText) itemText.textContent = item.text || '';
            const rawButton = article.querySelector('[data-raw-item]');
            if (rawButton) rawButton.addEventListener('click', () => loadRawSection(item.item, article, rawButton));
            for (const sectionButton of article.querySelectorAll('[data-raw-section-item]')) {{
              sectionButton.addEventListener('click', () => loadRawSection(sectionButton.dataset.rawSectionItem, sectionButton.closest('.structure-section'), sectionButton));
            }}
            items.appendChild(article);
          }}
        }}

        function renderRecoveryControls(itemResults) {{
          const actionable = [];
          for (const item of itemResults) {{
            for (const action of item.recommended_actions) {{
              actionable.push({{item, action}});
            }}
          }}
          if (!actionable.length) {{
            recoveryPanel.innerHTML = '';
            return;
          }}
          recoveryPanel.innerHTML = `
            <header class="panel-header">
              <div>
                <h2>Recovery actions</h2>
                <p class="muted">${{actionable.length}} actions generated from current extraction evidence.</p>
              </div>
            </header>
            <div class="recovery-actions"></div>
          `;
          const container = recoveryPanel.querySelector('.recovery-actions');
          for (const entry of actionable) {{
            const item = entry.item;
            const action = entry.action;
            const row = document.createElement('div');
            row.className = `recovery-action ${{escapeHtml(action.severity)}}`;
            const selector = action.reason === 'internal_item_toc_detected'
              ? `<label>Selection<select data-recovery-selection="${{escapeHtml(item.item)}}">${{action.options.map(option => `<option value="${{escapeHtml(option)}}">${{escapeHtml(option)}}</option>`).join('')}}</select></label>`
              : '';
            const reviewSnippets = renderReviewSnippets(item, action);
            const exhibitLinks = action.reason === 'exhibit_index_detected' ? renderExhibitLinkList(item) : '';
            row.innerHTML = `
              <div>
                <strong>Item ${{escapeHtml(item.item)}} | ${{escapeHtml(action.action_type)}}:${{escapeHtml(action.reason)}}</strong>
                <p>${{escapeHtml(action.description)}}</p>
                <small>${{escapeHtml(action.severity)}} | user input ${{action.requires_user_input ? 'yes' : 'no'}} | ${{escapeHtml(action.next_step || 'none')}}</small>
              </div>
              ${{reviewSnippets}}
              ${{exhibitLinks}}
              ${{selector}}
            `;
            container.appendChild(row);
          }}
        }}

        function renderStructureTags(rawStructure) {{
          const tags = [];
          const tableCount = Number(rawStructure.table_count || 0);
          const imageCount = Number(rawStructure.image_count || 0);
          if (tableCount > 0) tags.push(`<span class="structure-tag table">tables ${{tableCount}}</span>`);
          if (imageCount > 0) tags.push(`<span class="structure-tag image">images ${{imageCount}}</span>`);
          return tags.join('');
        }}

        function renderStructurePanel(item) {{
          const rawStructure = item.raw_structure || {{}};
          const rawSections = Array.isArray(rawStructure.sections) ? rawStructure.sections : [];
          const rawOutline = Array.isArray(rawStructure.outline) ? rawStructure.outline : [];
          const textOutline = outlineEntriesForText(item.text || '');
          const outline = rawSections.length ? rawSections.map(section => section.label) : (rawOutline.length ? rawOutline : textOutline);
          const rawBytes = Number(rawStructure.raw_bytes || 0);
          const tableCount = Number(rawStructure.table_count || 0);
          const shouldShow = rawSections.length || outline.length || rawBytes > 250000 || tableCount > 50;
          if (!shouldShow) return '';
          const sectionContent = rawSections.length
            ? `<div class="structure-section-list">${{rawSections.slice(0, 30).map((section, index) => renderStructureSection(section, index, item)).join('')}}</div>`
            : `<ol>${{outline.length ? outline.slice(0, 30).map(label => `<li>${{escapeHtml(label)}}</li>`).join('') : '<li>No bold/internal headings detected; use original filing structure for full review.</li>'}}</ol>`;
          return `
            <details class="structure-outline">
              <summary>Section structure</summary>
              <div class="structure-outline-meta">${{Number(rawBytes).toLocaleString()}} raw bytes | ${{tableCount}} tables | ${{Number(rawStructure.image_count || 0)}} images</div>
              ${{sectionContent}}
            </details>
          `;
        }}

        function renderStructureSection(section, index, item) {{
          const text = String(section.text || '').trim() || String(section.label || '').trim() || 'No text extracted for this subsection.';
          const tableCount = Number(section.table_count || 0);
          const imageCount = Number(section.image_count || 0);
          const rawItem = `${{item.item}}:${{index}}`;
          const label = section.href
            ? `<a href="${{escapeHtml(section.href)}}" target="_blank" rel="noopener noreferrer">${{escapeHtml(section.label || `Section ${{index + 1}}`)}}</a>`
            : `<span>${{escapeHtml(section.label || `Section ${{index + 1}}`)}}</span>`;
          return `
            <details class="structure-section" ${{index === 0 ? 'open' : ''}}>
              <summary>
                ${{label}}
                <small>${{Number(section.raw_bytes || 0).toLocaleString()}} bytes | ${{tableCount}} tables | ${{imageCount}} images</small>
              </summary>
              <pre class="structure-section-text extracted-view">${{escapeHtml(text)}}</pre>
              <div class="raw-section-tools nested">
                <button class="secondary-button compact" data-raw-section-item="${{escapeHtml(rawItem)}}">Show original filing structure</button>
                <span class="raw-section-meta"></span>
              </div>
              <div class="raw-section-preview nested" hidden></div>
            </details>
          `;
        }}

        function outlineEntriesForText(text) {{
          const result = [];
          const seen = new Set();
          const lines = String(text || '').split(/\\n+/).map(line => line.replace(/\\s+/g, ' ').trim()).filter(Boolean);
          for (const line of lines) {{
            if (result.length >= 30) break;
            if (!looksLikeOutlineLabel(line)) continue;
            const key = line.toLowerCase();
            if (seen.has(key)) continue;
            seen.add(key);
            result.push(line.slice(0, 140));
          }}
          return result;
        }}

        function looksLikeOutlineLabel(line) {{
          if (line.length < 8 || line.length > 160) return false;
          if (/^item\\s+/i.test(line)) return false;
          if (/\\.{2,}\\s*\\d+\\s*$/.test(line)) return false;
          if (/^[\\d.,$%()\\s-]+$/.test(line)) return false;
          const letters = (line.match(/[A-Za-z]/g) || []).length;
          if (letters < 5) return false;
          const uppercase = (line.match(/[A-Z]/g) || []).length / Math.max(letters, 1);
          return uppercase > 0.55 || (/^[A-Z]/.test(line) && !line.endsWith('.'));
        }}

        async function runRecovery() {{
          if (!lastExtraction) return;
          recoverButton.disabled = true;
          const selections = {{}};
          for (const select of document.querySelectorAll('[data-recovery-selection]')) {{
            selections[`${{filingId}}:${{select.dataset.recoverySelection}}`] = select.value;
          }}
          statusBanner.textContent = 'Running deterministic recovery actions...';
          const response = await fetch(`/api/filings/${{encodeURIComponent(filingId)}}/recover`, {{
            method: 'POST',
            cache: 'no-store',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{selections}})
          }});
          const payload = await response.json();
          if (!response.ok) {{
            statusBanner.textContent = `Recovery failed: ${{payload.error || 'unknown'}}`;
            recoverButton.disabled = false;
            return;
          }}
          renderRecoveryResults(payload);
          statusBanner.textContent = `Recovery complete | ${{payload.summary.recovery_actions}} actions | ${{payload.elapsed_ms}} ms`;
          recoverButton.disabled = false;
        }}

        function renderRecoveryResults(payload) {{
          const resultBlock = document.createElement('section');
          resultBlock.className = 'recovery-results';
          resultBlock.innerHTML = '<h2>Recovery results</h2>';
          for (const recovery of payload.recoveries) {{
            const card = document.createElement('article');
            card.className = `recovery-result ${{escapeHtml(recovery.status)}}`;
            const pageRange = recovery.page_range ? `${{recovery.page_range[0]}}-${{recovery.page_range[1]}}` : 'none';
            const selectedOption = recovery.selected_option || 'none';
            const actionButtons = recovery.extracted_text ? `
              <div class="review-decision-row">
                <button class="secondary-button compact" type="button" disabled>Keep original</button>
                <button class="secondary-button compact" type="button" disabled>Use reviewed candidate</button>
                <span class="muted">Review decision persistence is intentionally deferred.</span>
              </div>
            ` : '';
            card.innerHTML = `
              <h3>Item ${{escapeHtml(recovery.item)}} | ${{escapeHtml(recovery.reason)}}</h3>
              <p>${{escapeHtml(recovery.status)}} | ${{escapeHtml(recovery.severity)}} | ${{escapeHtml(recovery.next_step || 'none')}}</p>
              <p>Page range ${{escapeHtml(pageRange)}} | selection ${{escapeHtml(selectedOption)}} | before ${{Number(recovery.before_length || 0).toLocaleString()}} | after ${{recovery.after_length ? Number(recovery.after_length).toLocaleString() : 'none'}}</p>
              <p>${{escapeHtml(recovery.message)}}</p>
              <pre></pre>
              ${{actionButtons}}
            `;
            card.querySelector('pre').textContent = recovery.extracted_text ? edgeSnippet(recovery.extracted_text, 'start') + '\\n\\n' + edgeSnippet(recovery.extracted_text, 'end') : '';
            resultBlock.appendChild(card);
          }}
          recoveryPanel.appendChild(resultBlock);
        }}

        async function loadRawSection(itemId, container, triggerButton) {{
          const button = triggerButton || container.querySelector('[data-raw-item]');
          const toolRow = button.closest('.raw-section-tools');
          const meta = toolRow ? toolRow.querySelector('.raw-section-meta') : container.querySelector('.raw-section-meta');
          const preview = toolRow && toolRow.nextElementSibling?.classList.contains('raw-section-preview')
            ? toolRow.nextElementSibling
            : container.querySelector('.raw-section-preview');
          const extractedView = container.querySelector('.extracted-view');
          if (container.dataset.rawVisible === 'true') {{
            container.dataset.rawVisible = 'false';
            if (extractedView) extractedView.hidden = false;
            preview.hidden = true;
            button.textContent = 'Show original filing structure';
            meta.textContent = '';
            return;
          }}
          container.dataset.rawVisible = 'true';
          if (extractedView) extractedView.hidden = true;
          preview.hidden = false;
          button.textContent = 'Show extracted view';
          if (preview.dataset.loaded === 'true') {{
            meta.textContent = preview.dataset.meta || '';
            return;
          }}
          button.disabled = true;
          meta.textContent = 'Loading original HTML...';
          preview.innerHTML = '';
          try {{
            const response = await fetch(`/api/filings/${{encodeURIComponent(filingId)}}/raw-section/${{encodeURIComponent(itemId)}}`, {{cache: 'no-store'}});
            const payload = await response.json();
            if (!response.ok) throw new Error(payload.message || payload.error || 'raw_section_failed');
            meta.textContent = `${{payload.table_count}} tables | ${{payload.image_count}} images | ${{Number(payload.raw_bytes).toLocaleString()}} bytes`;
            preview.dataset.meta = meta.textContent;
            const iframe = document.createElement('iframe');
            iframe.className = 'raw-section-frame';
            iframe.setAttribute('sandbox', '');
            iframe.srcdoc = payload.srcdoc;
            preview.appendChild(iframe);
            preview.dataset.loaded = 'true';
          }} catch (error) {{
            meta.textContent = `Original view failed: ${{error.message}}`;
          }} finally {{
            button.disabled = false;
          }}
        }}

        function edgeSnippet(text, mode) {{
          const value = String(text || '').replace(/\\s+/g, ' ').trim();
          if (value.length <= 520) return value;
          return mode === 'end' ? value.slice(-520) : value.slice(0, 520);
        }}

        function renderReviewSnippets(item, action) {{
          if (!['section_reference_detected', 'exhibit_index_detected', 'external_or_other_document_reference'].includes(action.reason)) {{
            return '';
          }}
          const snippets = reviewSnippetsFor(item.text || '', action.reason);
          if (!snippets.length) {{
            return '';
          }}
          return `
            <details class="review-snippets" open>
              <summary>Review snippets</summary>
              ${{snippets.map(snippet => `<pre>${{escapeHtml(snippet)}}</pre>`).join('')}}
            </details>
          `;
        }}

        function reviewSnippetsFor(text, reason) {{
          const patterns = reason === 'exhibit_index_detected'
            ? [/\\bexhibit(?:s| index)?\\b/i, /\\bschedule(?:s)?\\b/i, /\\btable\\b/i]
            : [/\\bincorporated\\s+herein\\s+by\\s+reference\\b/i, /\\bsee\\s+(?:the\\s+)?(?:annual report|proxy statement|exhibit index|note\\s+\\d+|part\\s+[ivx]+|item\\s+\\d)/i, /\\brefer(?:red|s|ring)?\\s+to\\b/i, /\\bappears?\\s+on\\s+pages?\\s+\\d+/i];
          const lines = String(text || '').split(/\\n+/).map(line => line.replace(/\\s+/g, ' ').trim()).filter(Boolean);
          const snippets = [];
          for (let index = 0; index < lines.length && snippets.length < 4; index += 1) {{
            if (!patterns.some(pattern => pattern.test(lines[index]))) continue;
            const start = Math.max(0, index - 1);
            const end = Math.min(lines.length, index + 2);
            snippets.push(lines.slice(start, end).join('\\n'));
          }}
          if (!snippets.length && text.trim()) {{
            snippets.push(edgeSnippet(text, 'start'));
          }}
          return snippets;
        }}

        function renderExhibitLinkList(item) {{
          const sections = Array.isArray(item.raw_structure?.sections) ? item.raw_structure.sections : [];
          const links = sections.filter(section => section.href).slice(0, 12);
          if (!links.length) return '';
          return `
            <details class="review-snippets exhibit-links" open>
              <summary>Exhibit links</summary>
              <ul>
                ${{links.map(section => `<li><a href="${{escapeHtml(section.href)}}" target="_blank" rel="noopener noreferrer">${{escapeHtml(section.label || section.href)}}</a></li>`).join('')}}
              </ul>
            </details>
          `;
        }}
        </script>
        """,
    )


def _react_page(title: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Cache-Control" content="no-store">
  <title>{title}</title>
  <link rel="stylesheet" href="/assets/styles.css">
</head>
<body>
  <div id="root"></div>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="/assets/app.js"></script>
</body>
</html>"""


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Cache-Control" content="no-store">
  <title>{title}</title>
  <style>{_styles()}</style>
</head>
<body>
{body}
<script>
function escapeHtml(value) {{
  return String(value ?? '').replace(/[&<>"']/g, character => ({{
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }}[character]));
}}
function cssId(value) {{
  return String(value).replace(/[^a-zA-Z0-9_-]/g, '-');
}}
</script>
</body>
</html>"""


def _styles() -> str:
    return """
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #f6f7f9;
  color: #19212a;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: inherit; text-decoration: none; }
h1, h2, p { margin: 0; }
.muted { color: #647080; }
.home-shell { max-width: 1180px; margin: 0 auto; padding: 32px 24px; }
.selector-panel { display: grid; gap: 24px; }
.toolbar { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.toolbar h1 { font-size: 28px; line-height: 1.15; }
.toolbar-actions { display: flex; gap: 8px; align-items: center; }
.sec-intake-panel {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) 150px 150px auto;
  gap: 10px;
  align-items: end;
  padding: 14px;
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
}
.sec-intake-panel h2 { font-size: 18px; margin: 0 0 4px; }
.sec-intake-panel label { display: grid; gap: 4px; color: #44515f; font-size: 13px; }
.sec-intake-panel input,
.sec-intake-panel select {
  min-height: 36px;
  border: 1px solid #c9d1da;
  border-radius: 6px;
  padding: 0 10px;
  color: #19212a;
  background: #ffffff;
}
.sec-intake-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
.sec-intake-panel pre {
  grid-column: 1 / -1;
  max-height: 220px;
  overflow: auto;
  margin: 0;
  padding: 10px;
  border-radius: 6px;
  background: #f6f7f9;
  white-space: pre-wrap;
  font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.live-smoke-panel {
  display: grid;
  gap: 10px;
  padding: 14px;
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
}
.live-smoke-panel h2 { font-size: 18px; margin: 0 0 4px; }
.live-smoke-table {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
}
.live-smoke-table a {
  display: grid;
  gap: 4px;
  padding: 10px;
  border: 1px solid #d9dee5;
  border-radius: 6px;
  background: #fbfcfd;
}
.live-smoke-table a:hover { border-color: #1769aa; }
.live-smoke-table span { color: #647080; font-size: 13px; }
.live-smoke-panel pre,
.live-raw-panel pre {
  max-height: 320px;
  overflow: auto;
  margin: 10px 0 0;
  padding: 10px;
  border-radius: 6px;
  background: #f6f7f9;
  white-space: pre-wrap;
  font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.icon-button, .primary-button {
  border: 1px solid #c9d1da;
  background: #ffffff;
  color: #1e2a36;
  border-radius: 6px;
  min-height: 40px;
  padding: 0 14px;
  cursor: pointer;
}
.primary-button { background: #1769aa; border-color: #1769aa; color: white; width: 100%; }
.secondary-button {
  border: 1px solid #c9d1da;
  background: #ffffff;
  color: #1e2a36;
  border-radius: 6px;
  min-height: 40px;
  padding: 0 14px;
  cursor: pointer;
  width: 100%;
}
.secondary-button.compact {
  width: auto;
  min-height: 34px;
  padding: 0 10px;
}
.upload-form {
  display: grid;
  gap: 10px;
  margin: 16px 0;
}
.upload-form label {
  display: grid;
  gap: 4px;
  color: #44515f;
  font-size: 13px;
}
.upload-form input {
  min-height: 36px;
  width: 100%;
  border: 1px solid #c9d1da;
  border-radius: 6px;
  padding: 0 10px;
  color: #19212a;
  background: #ffffff;
}
.upload-form input[type="file"] {
  padding: 7px 8px;
}
.primary-button:disabled, .secondary-button:disabled { opacity: 0.55; cursor: wait; }
.filing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}
.filing-card {
  display: grid;
  gap: 8px;
  min-height: 112px;
  padding: 14px;
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
}
.filing-card:hover { border-color: #1769aa; }
.ticker { font-size: 22px; font-weight: 700; }
.meta { color: #44515f; }
.available { color: #137333; font-size: 13px; }
.missing { color: #a13b2b; font-size: 13px; }
.workspace-shell {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  min-height: 100vh;
}
.toc-panel {
  position: sticky;
  top: 0;
  align-self: start;
  height: 100vh;
  overflow: auto;
  padding: 18px;
  border-right: 1px solid #d9dee5;
  background: #ffffff;
}
.back-link { display: inline-block; margin-bottom: 18px; color: #1769aa; }
.toc-panel h1 { font-size: 22px; margin-bottom: 6px; overflow-wrap: anywhere; }
.toc-heading { font-size: 13px; margin: 18px 0 8px; color: #647080; text-transform: uppercase; }
.sidebar-actions { display: grid; gap: 8px; margin: 16px 0; }
.toc-list { display: grid; gap: 4px; }
.toc-link {
  display: grid;
  gap: 2px;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid transparent;
}
.toc-link:hover { border-color: #c9d1da; background: #f6f7f9; }
.toc-link span { font-weight: 700; }
.toc-link small { color: #647080; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.toc-link em { color: #647080; font-size: 12px; font-style: normal; }
.toc-link.not_present { opacity: 0.55; }
.toc-link.high { border-left: 3px solid #2d7d46; }
.toc-link.medium { border-left: 3px solid #b87900; }
.toc-link.low { border-left: 3px solid #c14f3d; }
.item-panel { min-width: 0; padding: 18px; }
.status-banner {
  position: sticky;
  top: 0;
  z-index: 2;
  margin-bottom: 12px;
  padding: 12px 14px;
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
}
.status-banner.error { border-color: #efc1b7; color: #a13b2b; background: #fff0ec; }
.metadata-panel, .recovery-panel { margin-bottom: 12px; }
.live-raw-panel { margin-top: 14px; }
.live-raw-panel details {
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
  padding: 10px 12px;
}
.live-raw-panel summary { cursor: pointer; color: #304255; }
.metadata-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  padding: 10px 12px;
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
  color: #44515f;
  font-size: 13px;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: start;
  padding: 12px 0;
}
.panel-header h2, .recovery-results h2 { font-size: 18px; margin: 0; }
.recovery-actions, .recovery-results { display: grid; gap: 8px; }
.recovery-action, .recovery-result {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
}
.recovery-action.blocked { border-left: 3px solid #c14f3d; }
.recovery-action.review { border-left: 3px solid #b87900; }
.recovery-action.info { border-left: 3px solid #1769aa; }
.recovery-action p, .recovery-action small, .recovery-result p { margin: 4px 0 0; color: #44515f; }
.recovery-action label { display: grid; gap: 4px; color: #44515f; font-size: 13px; }
.recovery-action select {
  max-width: 420px;
  min-height: 34px;
  border: 1px solid #c9d1da;
  border-radius: 6px;
  background: #ffffff;
  color: #19212a;
}
.review-snippets {
  border: 1px solid #e0e4e9;
  border-radius: 6px;
  background: #fbfcfd;
}
.review-snippets summary { cursor: pointer; padding: 8px 10px; color: #44515f; }
.review-snippets pre {
  max-height: 180px;
  overflow: auto;
  margin: 0;
  padding: 8px 10px;
  border-top: 1px solid #e0e4e9;
  white-space: pre-wrap;
  font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.review-snippets ul { margin: 0; padding: 0 12px 10px 28px; }
.review-snippets li { margin-bottom: 5px; overflow-wrap: anywhere; }
.review-snippets a { color: #1769aa; text-decoration: underline; }
.recovery-result h3 { margin: 0; font-size: 16px; }
.recovery-result pre {
  max-height: 220px;
  overflow: auto;
  margin: 0;
  padding: 10px;
  border-radius: 6px;
  background: #fbfcfd;
  white-space: pre-wrap;
}
.review-decision-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.items { display: grid; gap: 14px; }
.item-card {
  border: 1px solid #d9dee5;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}
.item-header { display: flex; justify-content: space-between; gap: 16px; align-items: start; }
.item-header h2 { font-size: 20px; }
.item-badges { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.pill {
  border-radius: 999px;
  padding: 4px 9px;
  font-size: 12px;
  border: 1px solid #c9d1da;
  background: #f6f7f9;
}
.pill.high { color: #137333; background: #edf7ee; border-color: #b8dfbd; }
.pill.medium { color: #8a5a00; background: #fff6dd; border-color: #efd48b; }
.pill.low { color: #a13b2b; background: #fff0ec; border-color: #efc1b7; }
.structure-tag {
  border-radius: 999px;
  padding: 4px 9px;
  font-size: 12px;
  border: 1px solid #c9d1da;
  background: #f6f7f9;
  color: #44515f;
}
.structure-tag.table { color: #155e75; border-color: #a5d8e6; background: #ecfeff; }
.structure-tag.image { color: #7c3d12; border-color: #f2c59b; background: #fff7ed; }
.evidence-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 14px 0;
}
.evidence-grid div {
  min-width: 0;
  padding: 10px;
  border-radius: 6px;
  background: #f6f7f9;
}
dt { font-size: 12px; color: #647080; margin-bottom: 4px; }
dd { margin: 0; overflow-wrap: anywhere; }
.chip-row { display: flex; gap: 6px; flex-wrap: wrap; }
.warning-chip, .action-chip, .empty-chip {
  display: inline-block;
  border-radius: 999px;
  padding: 3px 8px;
  font-size: 12px;
  border: 1px solid #c9d1da;
  background: #ffffff;
}
.warning-chip { color: #8a5a00; border-color: #efd48b; background: #fff6dd; }
.action-chip.blocked { color: #a13b2b; border-color: #efc1b7; background: #fff0ec; }
.action-chip.review { color: #8a5a00; border-color: #efd48b; background: #fff6dd; }
.action-chip.info { color: #1769aa; border-color: #b8d5ee; background: #edf5fb; }
.empty-chip { color: #647080; background: #f6f7f9; }
.snippet-details {
  border: 1px solid #e0e4e9;
  border-radius: 6px;
  margin-bottom: 12px;
  background: #fbfcfd;
}
.snippet-details summary { cursor: pointer; padding: 10px 12px; color: #44515f; }
.snippet-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  padding: 0 12px 12px;
}
.snippet-grid pre {
  margin: 0;
  max-height: 180px;
  overflow: auto;
  white-space: pre-wrap;
  font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.structure-outline {
  border: 1px solid #d8e1ea;
  border-radius: 6px;
  margin-bottom: 12px;
  background: #fbfcfd;
}
.structure-outline summary { cursor: pointer; padding: 10px 12px; color: #304255; }
.structure-outline-meta {
  padding: 0 12px 8px;
  color: #647080;
  font-size: 13px;
}
.structure-outline ol {
  margin: 0;
  padding: 0 12px 12px 32px;
  columns: 2;
  column-gap: 28px;
}
.structure-outline li {
  break-inside: avoid;
  margin-bottom: 5px;
  color: #19212a;
}
.structure-section-list {
  display: grid;
  gap: 8px;
  padding: 0 12px 12px;
}
.structure-section {
  border: 1px solid #e0e4e9;
  border-radius: 6px;
  background: #ffffff;
}
.structure-section summary {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: start;
  padding: 9px 10px;
  cursor: pointer;
}
.structure-section summary span,
.structure-section summary a {
  font-weight: 700;
  overflow-wrap: anywhere;
}
.structure-section summary a {
  color: #1769aa;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.structure-section summary small {
  flex: 0 0 auto;
  color: #647080;
  font-size: 12px;
  white-space: nowrap;
}
.structure-section pre {
  max-height: 260px;
  overflow: auto;
  margin: 0;
  padding: 10px;
  border-top: 1px solid #e0e4e9;
  background: #fbfcfd;
  white-space: pre-wrap;
  font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.raw-section-tools {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.raw-section-tools.nested {
  padding: 0 10px 10px;
  margin-bottom: 0;
}
.raw-section-meta { color: #647080; font-size: 13px; }
.raw-section-preview { margin-bottom: 12px; }
.raw-section-preview.nested {
  padding: 0 10px 10px;
}
.raw-section-preview.nested .raw-section-frame {
  min-height: 360px;
}
.raw-section-frame {
  width: 100%;
  min-height: 520px;
  border: 1px solid #c9d1da;
  border-radius: 6px;
  background: #ffffff;
}
.item-text {
  max-height: 460px;
  overflow: auto;
  margin: 0;
  padding: 12px;
  border: 1px solid #e0e4e9;
  border-radius: 6px;
  background: #fbfcfd;
  white-space: pre-wrap;
  font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.loading { padding: 18px; color: #647080; }
.loading.slim { padding: 10px; }
@media (max-width: 820px) {
  .workspace-shell { grid-template-columns: 1fr; }
  .sec-intake-panel { grid-template-columns: 1fr; }
  .toc-panel { position: relative; height: auto; border-right: 0; border-bottom: 1px solid #d9dee5; }
  .evidence-grid { grid-template-columns: 1fr; }
  .snippet-grid { grid-template-columns: 1fr; }
}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local SEC 10-K extraction review UI.")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), WebUiHandler)
    print(f"serving SEC 10-K extraction UI at http://{args.host}:{args.port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
