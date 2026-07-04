from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def record_hash(row: dict[str, object]) -> str:
    payload = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def should_include(row: dict[str, object], updated_since: str | None) -> bool:
    if not updated_since:
        return True
    event_timestamp = row.get("event_timestamp")
    if not isinstance(event_timestamp, str):
        return False
    return event_timestamp > updated_since


def extract_events(
    input_dir: Path,
    output_root: Path,
    batch_id: str,
    extracted_at: datetime,
    updated_since: str | None,
) -> Path:
    load_date = extracted_at.date().isoformat()
    output_dir = output_root / "events" / "product_events" / f"load_date={load_date}" / f"batch_id={batch_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "data.jsonl"

    total_rows = 0
    source_files = sorted(input_dir.glob("*.ndjson"))

    if not source_files:
        raise FileNotFoundError(f"No NDJSON files found in {input_dir}")

    with output_path.open("w", encoding="utf-8") as out:
        for source_file in source_files:
            with source_file.open("r", encoding="utf-8") as source:
                for line_number, line in enumerate(source, start=1):
                    line = line.strip()
                    if not line:
                        continue

                    row = json.loads(line)

                    if not isinstance(row, dict):
                        raise TypeError(f"Expected JSON object file={source_file} line={line_number}")

                    if not should_include(row, updated_since):
                        continue

                    enriched_row = {
                        **row,
                        "source_system": "product_events",
                        "source_entity": "product_events",
                        "source_table_or_endpoint": "product_events",
                        "source_file_path": str(source_file),
                        "batch_id": batch_id,
                        "extracted_at": extracted_at.isoformat(),
                        "load_date": load_date,
                        "raw_file_path": str(output_path),
                        "record_hash": record_hash(row),
                    }
                    out.write(json.dumps(enriched_row, sort_keys=True, ensure_ascii=False) + "\n")
                    total_rows += 1

    print(f"extracted source_files={len(source_files)} rows={total_rows} path={output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract product event NDJSON files to raw JSONL.")
    parser.add_argument("--input-dir", default="data/product_events")
    parser.add_argument("--output-root", default="raw")
    parser.add_argument("--updated-since", default=None)
    args = parser.parse_args()

    batch_id = str(uuid.uuid4())
    extracted_at = utc_now()

    print(f"batch_id={batch_id}")
    print(f"extracted_at={extracted_at.isoformat()}")
    print(f"input_dir={args.input_dir}")
    print(f"updated_since={args.updated_since}")

    extract_events(
        input_dir=Path(args.input_dir),
        output_root=Path(args.output_root),
        batch_id=batch_id,
        extracted_at=extracted_at,
        updated_since=args.updated_since,
    )


if __name__ == "__main__":
    main()
