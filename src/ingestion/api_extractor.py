from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

DEFAULT_ENDPOINTS = ["leads", "campaigns", "opportunities", "marketing_spend"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def record_hash(row: dict[str, object]) -> str:
    payload = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fetch_json(url: str, retries: int = 3, retry_sleep_seconds: float = 1.0) -> dict[str, object]:
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            with urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            print(f"request_failed attempt={attempt} url={url} error={exc}")
            if attempt < retries:
                time.sleep(retry_sleep_seconds * attempt)

    raise RuntimeError(f"request_failed_after_retries url={url}") from last_error


def extract_endpoint(
    base_url: str,
    endpoint: str,
    batch_id: str,
    extracted_at: datetime,
    output_root: Path,
    page_size: int,
    updated_since: str | None,
) -> Path:
    load_date = extracted_at.date().isoformat()
    output_dir = output_root / "api" / endpoint / f"load_date={load_date}" / f"batch_id={batch_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "data.jsonl"

    total_rows = 0
    page = 1
    has_next = True

    with output_path.open("w", encoding="utf-8") as f:
        while has_next:
            params = {
                "page": page,
                "page_size": page_size,
            }
            if updated_since:
                params["updated_since"] = updated_since

            url = f"{base_url.rstrip('/')}/{endpoint}?{urlencode(params)}"
            payload = fetch_json(url)
            records = payload.get("data", [])
            pagination = payload.get("pagination", {})

            if not isinstance(records, list):
                raise TypeError(f"Expected list for data endpoint={endpoint}")

            for row in records:
                if not isinstance(row, dict):
                    raise TypeError(f"Expected dict row endpoint={endpoint}")

                enriched_row = {
                    **row,
                    "source_system": "mock_crm_api",
                    "source_entity": endpoint,
                    "source_table_or_endpoint": endpoint,
                    "batch_id": batch_id,
                    "extracted_at": extracted_at.isoformat(),
                    "load_date": load_date,
                    "raw_file_path": str(output_path),
                    "record_hash": record_hash(row),
                }
                f.write(json.dumps(enriched_row, sort_keys=True, ensure_ascii=False) + "\n")
                total_rows += 1

            has_next = bool(pagination.get("has_next", False))
            page = int(pagination.get("next_page") or page + 1)

    print(f"extracted endpoint={endpoint} rows={total_rows} path={output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract mock CRM API endpoints to raw JSONL files.")
    parser.add_argument("--base-url", default=os.getenv("MOCK_CRM_API_BASE_URL", "http://localhost:8000"))
    parser.add_argument("--output-root", default="raw")
    parser.add_argument("--endpoints", nargs="*", default=DEFAULT_ENDPOINTS)
    parser.add_argument("--page-size", type=int, default=10)
    parser.add_argument("--updated-since", default=os.getenv("MOCK_CRM_UPDATED_SINCE"))
    args = parser.parse_args()

    batch_id = str(uuid.uuid4())
    extracted_at = utc_now()
    output_root = Path(args.output_root)

    print(f"batch_id={batch_id}")
    print(f"extracted_at={extracted_at.isoformat()}")
    print(f"base_url={args.base_url}")
    print(f"updated_since={args.updated_since}")

    for endpoint in args.endpoints:
        extract_endpoint(
            base_url=args.base_url,
            endpoint=endpoint,
            batch_id=batch_id,
            extracted_at=extracted_at,
            output_root=output_root,
            page_size=args.page_size,
            updated_since=args.updated_since,
        )


if __name__ == "__main__":
    main()
