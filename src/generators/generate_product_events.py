from __future__ import annotations

import argparse
import json
import random
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

EVENT_TYPES = [
    "login",
    "account_created",
    "invite_user",
    "create_project",
    "use_core_feature",
    "export_report",
    "upgrade_prompt_viewed",
    "billing_page_viewed",
    "cancellation_started",
]

FEATURES = ["dashboard", "forecasting", "commission_calc", "cohort_report", "revenue_waterfall"]


def iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def event_probability(event_type: str) -> float:
    return {
        "login": 0.55,
        "account_created": 0.02,
        "invite_user": 0.08,
        "create_project": 0.10,
        "use_core_feature": 0.35,
        "export_report": 0.12,
        "upgrade_prompt_viewed": 0.07,
        "billing_page_viewed": 0.06,
        "cancellation_started": 0.015,
    }[event_type]


def build_event(event_number: int, account_id: str, event_type: str, event_dt: datetime) -> dict[str, object]:
    user_number = ((event_number - 1) % 40) + 1
    payload: dict[str, object] = {
        "event_id": f"evt_{event_number:06d}",
        "account_id": account_id,
        "user_id": f"user_{user_number:03d}",
        "event_type": event_type,
        "event_timestamp": iso(event_dt),
        "session_id": f"sess_{event_number // 3:06d}",
        "device_type": ["desktop", "mobile", "tablet"][event_number % 3],
        "country": ["US", "BR", "GB", "DE", "MX"][event_number % 5],
    }

    if event_type == "use_core_feature":
        payload["feature_name"] = FEATURES[event_number % len(FEATURES)]
        payload["usage_count"] = 1 + (event_number % 5)
    elif event_type == "export_report":
        payload["report_type"] = ["mrr", "retention", "commission", "marketing_roi"][event_number % 4]
    elif event_type == "upgrade_prompt_viewed":
        payload["prompt_location"] = ["dashboard", "billing", "feature_gate"][event_number % 3]
    elif event_type == "cancellation_started":
        payload["cancellation_reason"] = ["too_expensive", "missing_feature", "low_usage"][event_number % 3]

    return payload


def generate_events(output_dir: Path, start_date: date, days: int, seed: int) -> list[Path]:
    random.seed(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    accounts = [f"acc_{i:03d}" for i in range(1, 16)]
    event_number = 1
    output_paths: list[Path] = []

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        output_path = output_dir / f"product_events_{current_date.isoformat()}.ndjson"
        rows_written = 0

        with output_path.open("w", encoding="utf-8") as f:
            for account_id in accounts:
                for event_type in EVENT_TYPES:
                    if random.random() <= event_probability(event_type):
                        seconds = random.randint(0, 86399)
                        event_dt = datetime.combine(current_date, time.min, tzinfo=timezone.utc) + timedelta(seconds=seconds)
                        event = build_event(event_number, account_id, event_type, event_dt)
                        f.write(json.dumps(event, sort_keys=True) + "\n")
                        event_number += 1
                        rows_written += 1

        if rows_written:
            output_paths.append(output_path)
            print(f"generated file={output_path} rows={rows_written}")

    print(f"generated_files={len(output_paths)}")
    print(f"generated_events={event_number - 1}")
    return output_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic product event NDJSON files.")
    parser.add_argument("--output-dir", default="data/product_events")
    parser.add_argument("--start-date", default="2026-01-01")
    parser.add_argument("--days", type=int, default=120)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    generate_events(
        output_dir=Path(args.output_dir),
        start_date=date.fromisoformat(args.start_date),
        days=args.days,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
