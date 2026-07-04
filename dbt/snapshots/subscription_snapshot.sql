{% snapshot subscription_snapshot %}

{{
    config(
      target_schema='snapshots',
      unique_key='subscription_id',
      strategy='timestamp',
      updated_at='updated_at'
    )
}}

select
    subscription_id,
    account_id,
    plan_id,
    subscription_status,
    started_at,
    ended_at,
    cancelled_at,
    updated_at
from {{ source('postgres_source', 'subscriptions') }}

{% endsnapshot %}
