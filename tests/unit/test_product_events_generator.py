import hashlib
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_EVENT_TYPES = {
    "login",
    "account_created",
    "invite_user",
    "create_project",
    "use_core_feature",
    "export_report",
    "upgrade_prompt_viewed",
    "billing_page_viewed",
    "cancellation_started",
}


def run_generator(output_dir: Path, seed: int = 42) -> None:
    subprocess.run(
        [
            sys.executable,
            "src/generators/generate_product_events.py",
            "--output-dir",
            str(output_dir),
            "--start-date",
            "2026-01-01",
            "--days",
            "3",
            "--seed",
            str(seed),
        ],
        cwd=PROJECT_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def read_events(output_dir: Path) -> list[dict]:
    events: list[dict] = []

    for file_path in sorted(output_dir.glob("*.ndjson")):
        for line in file_path.read_text().splitlines():
            if line.strip():
                events.append(json.loads(line))

    return events


def directory_hash(output_dir: Path) -> str:
    digest = hashlib.sha256()

    for file_path in sorted(output_dir.glob("*.ndjson")):
        digest.update(file_path.name.encode())
        digest.update(file_path.read_bytes())

    return digest.hexdigest()


def test_product_event_generator_creates_one_file_per_day(tmp_path: Path) -> None:
    run_generator(tmp_path)

    files = sorted(tmp_path.glob("*.ndjson"))

    assert len(files) == 3


def test_product_event_generator_outputs_valid_json_events(tmp_path: Path) -> None:
    run_generator(tmp_path)

    events = read_events(tmp_path)

    assert events
    assert all(isinstance(event, dict) for event in events)


def test_product_event_generator_produces_unique_event_ids(tmp_path: Path) -> None:
    run_generator(tmp_path)

    events = read_events(tmp_path)
    event_ids = [event["event_id"] for event in events]

    assert len(event_ids) == len(set(event_ids))


def test_product_event_generator_uses_expected_event_types(tmp_path: Path) -> None:
    run_generator(tmp_path)

    events = read_events(tmp_path)
    event_types = {event["event_type"] for event in events}

    assert event_types
    assert event_types.issubset(ALLOWED_EVENT_TYPES)


def test_product_event_generator_is_deterministic_for_same_seed(tmp_path: Path) -> None:
    first_output = tmp_path / "first"
    second_output = tmp_path / "second"

    run_generator(first_output, seed=123)
    run_generator(second_output, seed=123)

    assert directory_hash(first_output) == directory_hash(second_output)


def test_product_event_generator_includes_required_fields(tmp_path: Path) -> None:
    run_generator(tmp_path)

    events = read_events(tmp_path)
    required_fields = {
        "event_id",
        "account_id",
        "user_id",
        "event_type",
        "event_timestamp",
        "session_id",
        "device_type",
        "country",
    }

    assert events
    assert required_fields.issubset(events[0].keys())
