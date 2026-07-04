create schema if not exists source;

create table if not exists source.accounts (
    account_id text primary key,
    account_name text,
    industry text,
    company_size text,
    country text,
    created_at timestamp,
    updated_at timestamp
);

create table if not exists source.customers (
    customer_id text primary key,
    account_id text,
    email text,
    full_name text,
    country text,
    signup_date date,
    created_at timestamp,
    updated_at timestamp,
    is_deleted boolean
);

create table if not exists source.plans (
    plan_id text primary key,
    plan_name text,
    billing_interval text,
    monthly_price numeric(12,2),
    currency text,
    is_active boolean
);

create table if not exists source.subscriptions (
    subscription_id text primary key,
    account_id text,
    plan_id text,
    subscription_status text,
    started_at timestamp,
    ended_at timestamp,
    cancelled_at timestamp,
    updated_at timestamp
);

create table if not exists source.invoices (
    invoice_id text primary key,
    account_id text,
    subscription_id text,
    invoice_date date,
    due_date date,
    status text,
    currency text,
    amount_due numeric(12,2),
    amount_paid numeric(12,2),
    created_at timestamp,
    updated_at timestamp
);

create table if not exists source.payments (
    payment_id text primary key,
    invoice_id text,
    account_id text,
    payment_date timestamp,
    payment_status text,
    payment_method text,
    amount numeric(12,2),
    currency text,
    failure_reason text,
    created_at timestamp
);

create table if not exists source.refunds (
    refund_id text primary key,
    payment_id text,
    account_id text,
    refund_date timestamp,
    amount numeric(12,2),
    reason text,
    created_at timestamp
);

create table if not exists source.sales_reps (
    sales_rep_id text primary key,
    sales_rep_name text,
    team text,
    region text,
    hire_date date,
    is_active boolean
);

create table if not exists source.sales_targets (
    target_id text primary key,
    sales_rep_id text,
    target_month date,
    target_revenue numeric(12,2),
    target_new_customers integer,
    created_at timestamp
);
