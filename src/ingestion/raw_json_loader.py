from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg

CREATE_SCHEMA_SQL = "create schema if not exists raw;"

CREATE_TABLE_SQL = """
create table if not exists raw.json_records (
    source_system text not null,
    source_entity text not null,
    source_table_or_endpoint text not null,
    record_hash text not null,
    batch_id text not null,
    extracted_at timestamp with time zone,
    load_date date,
    raw_file_path text not null,
    source_file_path text,
    payload jsonb not null,
    loaded_at timestamp with time zone not null,
    primary key (source_system, source_entity, record_hash)
);
"""


INSERT_SQL = """
insert into raw.json_records (
    source_system,
    source_entity,
    source_table_or_endpoint,
    record_hash,
    batch_id,
    extracted_at,
    load_date,
    raw_file_path,
    source_file_path,
    payload,
    loaded_at
)
values (
    %(source_system)s,
    %(source_entity)s,
    %(source_table_or_endpoint)s,
    %(record_hash)s,
    %(batch_id)s,
    %(extracted_at)s,
    %(load_date)s,
    %(raw_file_path)s,
    %(source_file_path)s,
    %(payload)s::jsonb,
    %(loaded_at)s
)
on conflict (source_system, source_entity, record_hash) do nothing;
"""


def connection_string() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "revopspulse")
    user = os.getenv("POSTGRES_USER", "revopspulse")
    password = os.getenv("POSTGRES_PASSWORD", "revopspulse")
    return f"host={host} port={port} dbname={db} user={user} password={password}"


def iter_jsonl_files(input_root: Path) -> list[Path]:
    return sorted(input_root.glob("**/*.jsonl"))


def normalize_record(row: dict[str, Any], loaded_at: datetime) -> dict[str, Any]:
    source_entity = row.get("source_entity")
    source_table_or_endpoint = row.get("source_table_or_endpoint") or source_entity

    normalized = {
        "source_system": row.get("source_system"),
        "source_entity": source_entity,
        "source_table_or_endpoint": source_table_or_endpoint,
        "record_hash": row.get("record_hash"),
        "batch_id": row.get("batch_id"),
        "extracted_at": row.get("extracted_at"),
        "load_date": row.get("load_date"),
        "raw_file_path": row.get("raw_file_path"),
        "source_file_path": row.get("source_file_path"),
        "payload": json.dumps(row, sort_keys=True, ensure_ascii=False),
        "loaded_at": loaded_at.isoformat(),
    }

    required_fields = [
        "source_system",
        "source_entity",
        "source_table_or_endpoint",
        "record_hash",
        "batch_id",
        "raw_file_path",
    ]

    missing = [field for field in required_fields if not normalized.get(field)]
    if missing:
        raise ValueError(f"Missing required metadata fields: {missing}")

    return normalized


def load_jsonl_files(input_root: Path) -> None:
    files = iter_jsonl_files(input_root)
    if not files:
        raise FileNotFoundError(f"No JSONL files found under {input_root}")

    loaded_at = datetime.now(timezone.utc)
    seen_rows = 0
    inserted_rows = 0

    with psycopg.connect(connection_string()) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_SCHEMA_SQL)
            cur.execute(CREATE_TABLE_SQL)

            for file_path in files:
                file_seen_rows = 0
                file_inserted_rows = 0

                with file_path.open("r", encoding="utf-8") as f:
                    for line_number, line in enumerate(f, start=1):
                        line = line.strip()
                        if not line:
                            continue

                        row = json.loads(line)
                        if not isinstance(row, dict):
                            raise TypeError(f"Expected JSON object file={file_path} line={line_number}")

                        cur.execute(INSERT_SQL, normalize_record(row, loaded_at))

                        file_seen_rows += 1
                        seen_rows += 1

                        inserted = cur.rowcount == 1
                        if inserted:
                            file_inserted_rows += 1
                            inserted_rows += 1

                print("loaded file=" f"{file_path} seen_rows={file_seen_rows} inserted_rows={file_inserted_rows}")

        conn.commit()

    print(f"jsonl_files={len(files)}")
    print(f"seen_rows={seen_rows}")
    print(f"inserted_rows={inserted_rows}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load RAW JSONL files into Postgres raw.json_records.")
    parser.add_argument("--input-root", required=True)
    args = parser.parse_args()

    load_jsonl_files(Path(args.input_root))


if __name__ == "__main__":
    main()
