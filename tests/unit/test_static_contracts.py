from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_mock_api_defines_required_endpoint_entities() -> None:
    source = (PROJECT_ROOT / "src/api_mock/mock_crm_api.py").read_text()

    for endpoint in ["health", "leads", "campaigns", "opportunities", "marketing_spend"]:
        assert endpoint in source


def test_mock_api_mentions_pagination_and_incremental_filtering() -> None:
    source = (PROJECT_ROOT / "src/api_mock/mock_crm_api.py").read_text()

    assert "page" in source
    assert "page_size" in source
    assert "updated_since" in source


def test_source_schema_contains_required_oltp_tables() -> None:
    ddl = (PROJECT_ROOT / "sql/init/001_create_source_schema.sql").read_text()

    for table_name in [
        "accounts",
        "customers",
        "plans",
        "subscriptions",
        "invoices",
        "payments",
        "refunds",
        "sales_reps",
        "sales_targets",
    ]:
        assert f"source.{table_name}" in ddl


def test_seed_file_documents_intentional_quality_cases() -> None:
    seed_sql = (PROJECT_ROOT / "sql/seed/002_seed_source_data.sql").read_text()

    assert "duplicate@example.com" in seed_sql
    assert "truncate table source.refunds" in seed_sql
