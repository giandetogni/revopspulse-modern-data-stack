from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from math import ceil
from urllib.parse import parse_qs, urlparse

HOST = "0.0.0.0"
PORT = 8000
BASE_DATE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def generate_leads() -> list[dict[str, object]]:
    records = []
    statuses = ["new", "qualified", "disqualified", "converted"]
    sources = ["paid_search", "organic", "linkedin", "referral", "webinar"]

    for i in range(1, 49):
        created_at = BASE_DATE + timedelta(days=i * 2)
        updated_at = created_at + timedelta(days=i % 11)
        records.append(
            {
                "lead_id": f"lead_{i:03d}",
                "email": f"lead{i:03d}@example.com",
                "company_name": f"Lead Company {i:03d}",
                "country": ["US", "BR", "GB", "DE", "MX"][i % 5],
                "lead_source": sources[i % len(sources)],
                "status": statuses[i % len(statuses)],
                "campaign_id": f"camp_{(i % 8) + 1:03d}",
                "created_at": iso(created_at),
                "updated_at": iso(updated_at),
            }
        )

    return records


def generate_campaigns() -> list[dict[str, object]]:
    channels = ["paid_search", "linkedin", "webinar", "content", "partner"]
    records = []

    for i in range(1, 9):
        start_date = BASE_DATE + timedelta(days=i * 5)
        updated_at = start_date + timedelta(days=30 + i)
        records.append(
            {
                "campaign_id": f"camp_{i:03d}",
                "campaign_name": f"Q1 Growth Campaign {i:03d}",
                "channel": channels[i % len(channels)],
                "target_segment": ["smb", "mid_market", "enterprise"][i % 3],
                "start_date": start_date.date().isoformat(),
                "end_date": (start_date + timedelta(days=45)).date().isoformat(),
                "updated_at": iso(updated_at),
            }
        )

    return records


def generate_opportunities() -> list[dict[str, object]]:
    stages = ["prospecting", "qualified", "proposal", "closed_won", "closed_lost"]
    records = []

    for i in range(1, 37):
        created_at = BASE_DATE + timedelta(days=i * 3)
        updated_at = created_at + timedelta(days=7 + (i % 20))
        close_date = created_at + timedelta(days=20 + (i % 30))
        stage = stages[i % len(stages)]

        records.append(
            {
                "opportunity_id": f"opp_{i:03d}",
                "account_id": f"acc_{((i - 1) % 15) + 1:03d}",
                "lead_id": f"lead_{((i - 1) % 48) + 1:03d}",
                "sales_rep_id": f"rep_{((i - 1) % 3) + 1:03d}",
                "campaign_id": f"camp_{((i - 1) % 8) + 1:03d}",
                "stage": stage,
                "amount": float(1200 + (i * 175)),
                "probability": {
                    "prospecting": 0.15,
                    "qualified": 0.35,
                    "proposal": 0.65,
                    "closed_won": 1.0,
                    "closed_lost": 0.0,
                }[stage],
                "created_at": iso(created_at),
                "close_date": close_date.date().isoformat(),
                "updated_at": iso(updated_at),
            }
        )

    return records


def generate_marketing_spend() -> list[dict[str, object]]:
    records = []

    for i in range(1, 49):
        spend_date = BASE_DATE + timedelta(days=i * 3)
        updated_at = spend_date + timedelta(days=i % 5)
        records.append(
            {
                "spend_id": f"spend_{i:03d}",
                "campaign_id": f"camp_{((i - 1) % 8) + 1:03d}",
                "spend_date": spend_date.date().isoformat(),
                "amount": float(250 + (i % 9) * 80),
                "currency": "USD",
                "updated_at": iso(updated_at),
            }
        )

    return records


DATASETS = {
    "leads": generate_leads(),
    "campaigns": generate_campaigns(),
    "opportunities": generate_opportunities(),
    "marketing_spend": generate_marketing_spend(),
}


class MockCRMHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")

    def send_json(self, status_code: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        endpoint = parsed.path.strip("/")

        if endpoint == "health":
            self.send_json(200, {"status": "ok", "service": "mock_crm_api"})
            return

        if endpoint not in DATASETS:
            self.send_json(404, {"error": "not_found", "available_endpoints": sorted(DATASETS)})
            return

        params = parse_qs(parsed.query)
        page = int(params.get("page", ["1"])[0])
        page_size = int(params.get("page_size", ["10"])[0])
        updated_since = params.get("updated_since", [None])[0]

        records = DATASETS[endpoint]

        if updated_since:
            records = [row for row in records if row["updated_at"] > updated_since]

        total_records = len(records)
        total_pages = ceil(total_records / page_size) if total_records else 0
        start = (page - 1) * page_size
        end = start + page_size
        page_records = records[start:end]

        self.send_json(
            200,
            {
                "data": page_records,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_records": total_records,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "next_page": page + 1 if page < total_pages else None,
                },
            },
        )


def main() -> None:
    server = HTTPServer((HOST, PORT), MockCRMHandler)
    print(f"mock_crm_api listening on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
