import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def write_input_events(input_dir: Path) -> None:
    input_dir.mkdir(parents=True, exist_ok=True)

    events = [
        {
            "event_id": "evt_old",
            "account_id": "acc_001",
            "user_id": "user_001",
            "event_type": "login",
            "event_timestamp": "2026-01-31T23:59:59Z",
            "session_id": "sess_old",
            "device_type": "desktop",
            "country": "US",
        },
        {
            "event_id": "evt_new",
            "account_id": "acc_001",
            "user_id": "user_001",
            "event_type": "use_core_feature",
            "event_timestamp": "2026-02-02T00:00:00Z",
            "session_id": "sess_new",
            "device_type": "desktop",
            "country": "US",
            "feature_name": "core_dashboard",
            "usage_count": 3,
        },
    ]

    file_path = input_dir / "product_events_2026-02-02.ndjson"
    file_path.write_text("\n".join(json.dumps(event) for event in events) + "\n")


def run_events_extractor(input_dir: Path, output_root: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "src/ingestion/events_extractor.py",
            "--input-dir",
            str(input_dir),
            "--output-root",
            str(output_root),
            "--updated-since",
            "2026-02-01T00:00:00Z",
        ],
        cwd=PROJECT_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def read_extracted_rows(output_root: Path) -> list[dict]:
    files = sorted((output_root / "events" / "product_events").rglob("data.jsonl"))

    assert files, "Expected events extractor to write a data.jsonl file."

    rows: list[dict] = []
    for line in files[-1].read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))

    return rows


def test_events_extractor_filters_events_by_updated_since(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_root = tmp_path / "raw"

    write_input_events(input_dir)
    run_events_extractor(input_dir, output_root)

    rows = read_extracted_rows(output_root)
    event_ids = {row["event_id"] for row in rows}

    assert "evt_new" in event_ids
    assert "evt_old" not in event_ids


def test_events_extractor_adds_required_raw_metadata(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_root = tmp_path / "raw"

    write_input_events(input_dir)
    run_events_extractor(input_dir, output_root)

    row = read_extracted_rows(output_root)[0]

    required_metadata = {
        "source_system",
        "source_entity",
        "source_table_or_endpoint",
        "source_file_path",
        "batch_id",
        "extracted_at",
        "load_date",
        "raw_file_path",
        "record_hash",
    }

    assert required_metadata.issubset(row.keys())
    assert row["source_system"] == "product_events"
    assert row["source_entity"] == "product_events"


def test_events_extractor_record_hash_is_sha256_like(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_root = tmp_path / "raw"

    write_input_events(input_dir)
    run_events_extractor(input_dir, output_root)

    row = read_extracted_rows(output_root)[0]

    assert len(row["record_hash"]) == 64
    int(row["record_hash"], 16)
