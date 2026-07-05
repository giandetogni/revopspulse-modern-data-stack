from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
random.seed(SEED)

OUTPUT_PATH = Path("sql/seed/002_seed_source_data.sql")


def sql_str(value: str | None) -> str:
    if value is None:
        return "null"
    return "'" + value.replace("'", "''") + "'"


def sql_bool(value: bool) -> str:
    return "true" if value else "false"


def sql_date(value: date | datetime | None) -> str:
    if value is None:
        return "null"
    return sql_str(value.isoformat())


def money(value: float) -> str:
    return f"{value:.2f}"


def main() -> None:
    base_date = date(2026, 1, 1)
    now = datetime(2026, 7, 4, 12, 0, 0)

    plans = [
        ("plan_starter", "Starter", "monthly", 49.00, "USD", True),
        ("plan_growth", "Growth", "monthly", 149.00, "USD", True),
        ("plan_scale", "Scale", "monthly", 399.00, "USD", True),
    ]

    sales_reps = [
        ("rep_001", "Alex Morgan", "SMB", "North America", date(2024, 3, 1), True),
        ("rep_002", "Bianca Silva", "Mid-Market", "LATAM", date(2023, 8, 15), True),
        ("rep_003", "Carlos Rivera", "Enterprise", "EMEA", date(2022, 11, 10), True),
    ]

    industries = ["fintech", "healthcare", "education", "retail", "logistics"]
    sizes = ["1-10", "11-50", "51-200", "201-500"]
    countries = ["US", "BR", "MX", "GB", "DE"]

    accounts = []
    customers = []
    subscriptions = []
    invoices = []
    payments = []
    refunds = []
    sales_targets = []

    for i in range(1, 16):
        account_id = f"acc_{i:03d}"
        created_at = datetime.combine(base_date + timedelta(days=i * 5), datetime.min.time())
        updated_at = created_at + timedelta(days=random.randint(1, 120))

        accounts.append(
            (
                account_id,
                f"Account {i:03d}",
                random.choice(industries),
                random.choice(sizes),
                random.choice(countries),
                created_at,
                updated_at,
            )
        )

        for j in range(1, random.randint(2, 4)):
            customer_id = f"cus_{i:03d}_{j:02d}"
            email = f"user{j}@account{i:03d}.com"

            if i == 2 and j == 1:
                email = "duplicate@example.com"
            if i == 3 and j == 1:
                email = "duplicate@example.com"

            customers.append(
                (
                    customer_id,
                    account_id,
                    email,
                    f"User {j} Account {i:03d}",
                    random.choice(countries),
                    created_at.date(),
                    created_at,
                    updated_at,
                    False,
                )
            )

        plan = random.choice(plans)
        plan_id = plan[0]
        monthly_price = plan[3]

        subscription_id = f"sub_{i:03d}"
        started_at = created_at + timedelta(days=3)
        status = random.choice(["active", "active", "active", "cancelled", "past_due", "trialing"])

        cancelled_at = None
        ended_at = None
        if status == "cancelled":
            cancelled_at = started_at + timedelta(days=random.randint(30, 120))
            ended_at = cancelled_at

        if i == 5:
            ended_at = started_at - timedelta(days=2)

        subscriptions.append(
            (
                subscription_id,
                account_id,
                plan_id,
                status,
                started_at,
                ended_at,
                cancelled_at,
                updated_at,
            )
        )

        for month_offset in range(0, 4):
            invoice_date = started_at.date() + timedelta(days=30 * month_offset)
            invoice_id = f"inv_{i:03d}_{month_offset + 1:02d}"
            invoice_status = random.choice(["paid", "paid", "paid", "open", "uncollectible"])
            amount_due = monthly_price
            amount_paid = amount_due if invoice_status == "paid" else 0.00

            if i == 6 and month_offset == 0:
                amount_due = -99.00

            invoices.append(
                (
                    invoice_id,
                    account_id,
                    subscription_id,
                    invoice_date,
                    invoice_date + timedelta(days=7),
                    invoice_status,
                    "USD",
                    amount_due,
                    amount_paid,
                    datetime.combine(invoice_date, datetime.min.time()),
                    datetime.combine(invoice_date, datetime.min.time()) + timedelta(hours=1),
                )
            )

            payment_id = f"pay_{i:03d}_{month_offset + 1:02d}"
            payment_status = "succeeded" if invoice_status == "paid" else random.choice(["failed", "pending"])
            failure_reason = None if payment_status == "succeeded" else "card_declined"

            invoice_ref = invoice_id
            if i == 7 and month_offset == 0:
                invoice_ref = None

            payments.append(
                (
                    payment_id,
                    invoice_ref,
                    account_id,
                    datetime.combine(invoice_date, datetime.min.time()) + timedelta(days=1),
                    payment_status,
                    random.choice(["card", "bank_transfer"]),
                    amount_paid if payment_status == "succeeded" else amount_due,
                    "USD",
                    failure_reason,
                    datetime.combine(invoice_date, datetime.min.time()),
                )
            )

            if payment_status == "succeeded" and random.random() < 0.12:
                refund_amount = round(amount_paid * random.choice([0.25, 0.50, 1.00]), 2)
                if i == 8 and month_offset == 0:
                    refund_amount = amount_paid + 50

                refunds.append(
                    (
                        f"ref_{i:03d}_{month_offset + 1:02d}",
                        payment_id,
                        account_id,
                        datetime.combine(invoice_date, datetime.min.time()) + timedelta(days=10),
                        refund_amount,
                        random.choice(["customer_request", "billing_error"]),
                        datetime.combine(invoice_date, datetime.min.time()) + timedelta(days=10),
                    )
                )

    for rep in sales_reps:
        for month in range(1, 5):
            sales_targets.append(
                (
                    f"target_{rep[0]}_{month:02d}",
                    rep[0],
                    date(2026, month, 1),
                    random.choice([8000.00, 10000.00, 15000.00]),
                    random.choice([5, 8, 10]),
                    now,
                )
            )

    lines = [
        "truncate table source.refunds, source.payments, source.invoices, source.subscriptions, source.customers, source.accounts, source.plans, source.sales_targets, source.sales_reps restart identity;",
        "",
    ]

    for row in plans:
        lines.append(
            "insert into source.plans values "
            f"({sql_str(row[0])}, {sql_str(row[1])}, {sql_str(row[2])}, {money(row[3])}, {sql_str(row[4])}, {sql_bool(row[5])});"
        )

    for row in sales_reps:
        lines.append(
            "insert into source.sales_reps values "
            f"({sql_str(row[0])}, {sql_str(row[1])}, {sql_str(row[2])}, {sql_str(row[3])}, {sql_date(row[4])}, {sql_bool(row[5])});"
        )

    for row in accounts:
        lines.append(
            "insert into source.accounts values "
            f"({sql_str(row[0])}, {sql_str(row[1])}, {sql_str(row[2])}, {sql_str(row[3])}, {sql_str(row[4])}, {sql_date(row[5])}, {sql_date(row[6])});"
        )

    for row in customers:
        lines.append(
            "insert into source.customers values "
            f"({sql_str(row[0])}, {sql_str(row[1])}, {sql_str(row[2])}, {sql_str(row[3])}, {sql_str(row[4])}, {sql_date(row[5])}, {sql_date(row[6])}, {sql_date(row[7])}, {sql_bool(row[8])});"
        )

    for row in subscriptions:
        lines.append(
            "insert into source.subscriptions values "
            f"({sql_str(row[0])}, {sql_str(row[1])}, {sql_str(row[2])}, {sql_str(row[3])}, {sql_date(row[4])}, {sql_date(row[5])}, {sql_date(row[6])}, {sql_date(row[7])});"
        )

    for row in invoices:
        lines.append(
            "insert into source.invoices values "
            f"({sql_str(row[0])}, {sql_str(row[1])}, {sql_str(row[2])}, {sql_date(row[3])}, {sql_date(row[4])}, {sql_str(row[5])}, {sql_str(row[6])}, {money(row[7])}, {money(row[8])}, {sql_date(row[9])}, {sql_date(row[10])});"
        )

    for row in payments:
        lines.append(
            "insert into source.payments values "
            f"({sql_str(row[0])}, {sql_str(row[1])}, {sql_str(row[2])}, {sql_date(row[3])}, {sql_str(row[4])}, {sql_str(row[5])}, {money(row[6])}, {sql_str(row[7])}, {sql_str(row[8])}, {sql_date(row[9])});"
        )

    for row in refunds:
        lines.append(
            "insert into source.refunds values "
            f"({sql_str(row[0])}, {sql_str(row[1])}, {sql_str(row[2])}, {sql_date(row[3])}, {money(row[4])}, {sql_str(row[5])}, {sql_date(row[6])});"
        )

    for row in sales_targets:
        lines.append(
            "insert into source.sales_targets values "
            f"({sql_str(row[0])}, {sql_str(row[1])}, {sql_date(row[2])}, {money(row[3])}, {row[4]}, {sql_date(row[5])});"
        )

    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")
    print(
        f"accounts={len(accounts)} customers={len(customers)} subscriptions={len(subscriptions)} invoices={len(invoices)} payments={len(payments)} refunds={len(refunds)}"
    )


if __name__ == "__main__":
    main()
