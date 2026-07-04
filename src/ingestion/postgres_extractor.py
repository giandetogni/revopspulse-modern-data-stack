from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_TABLES = [
    "accounts",
    "customers",
    "plans",
    "subscriptions",
    "invoices",
    "payments",
    "refunds",
    "sales_reps",
    "sales_targets",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def record_hash(row: dict[str, str]) -> str:
    payload = json.dumps(row, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def extract_table(table_name: str, batch_id: str, extracted_at: datetime, output_root: Path) -> Path:
    load_date = extracted_at.date().isoformat()

    output_dir = output_root / "postgres" / table_name / f"load_date={load_date}" / f"batch_id={batch_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "data.csv"

    sql = f"copy (select * from source.{table_name}) to stdout with csv header"

    result = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            "revopspulse-postgres",
            "psql",
            "-U",
            "revopspulse",
            "-d",
            "revopspulse",
            "-c",
            sql,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    source_lines = result.stdout.splitlines()
    reader = csv.DictReader(source_lines)

    rows_written = 0

    with output_path.open("w", newline="", encoding="utf-8") as f:
        source_fieldnames = reader.fieldnames or []
        metadata_fieldnames = [
            "source_system",
            "source_table_or_endpoint",
            "batch_id",
            "extracted_at",
            "load_date",
            "raw_file_path",
            "record_hash",
        ]

        writer = csv.DictWriter(f, fieldnames=source_fieldnames + metadata_fieldnames)
        writer.writeheader()

        for row in reader:
            row_hash = record_hash(row)

            enriched_row = {
                **row,
                "source_system": "postgres",
                "source_table_or_endpoint": table_name,
                "batch_id": batch_id,
                "extracted_at": extracted_at.isoformat(),
                "load_date": load_date,
                "raw_file_path": str(output_path),
                "record_hash": row_hash,
            }

            writer.writerow(enriched_row)
            rows_written += 1

    print(f"extracted table={table_name} rows={rows_written} path={output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract PostgreSQL source tables to raw CSV files.")
    parser.add_argument("--output-root", default="raw", help="Raw output root directory.")
    parser.add_argument("--tables", nargs="*", default=DEFAULT_TABLES, help="Tables to extract from source schema.")
    args = parser.parse_args()

    batch_id = str(uuid.uuid4())
    extracted_at = utc_now()
    output_root = Path(args.output_root)

    print(f"batch_id={batch_id}")
    print(f"extracted_at={extracted_at.isoformat()}")

    for table in args.tables:
        extract_table(table, batch_id, extracted_at, output_root)


if __name__ == "__main__":
    main()
