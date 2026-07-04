with events as (
    select * from {{ ref('stg_events__product_events') }}
)

select
    account_id,
    event_date,
    count(*) as total_events,
    count(distinct user_id) as active_users,
    count(distinct session_id) as sessions,
    count(*) filter (where event_type = 'login') as login_events,
    count(*) filter (where event_type = 'use_core_feature') as core_feature_events,
    count(*) filter (where event_type = 'create_project') as project_created_events,
    count(*) filter (where event_type = 'invite_user') as invite_user_events,
    count(*) filter (where event_type = 'export_report') as export_report_events,
    count(*) filter (where event_type = 'upgrade_prompt_viewed') as upgrade_prompt_viewed_events,
    count(*) filter (where event_type = 'billing_page_viewed') as billing_page_viewed_events,
    count(*) filter (where event_type = 'cancellation_started') as cancellation_started_events,
    sum(coalesce(usage_count, 0)) as total_feature_usage_count,
    min(event_timestamp) as first_event_at,
    max(event_timestamp) as last_event_at
from events
group by 1, 2
