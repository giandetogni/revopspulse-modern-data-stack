with date_bounds as (
    select
        min(event_date) as min_date,
        max(event_date) as max_date
    from {{ ref('fact_product_events') }}
),

date_spine as (
    select generate_series(
        min_date,
        max_date,
        interval '1 day'
    )::date as usage_date
    from date_bounds
),

account_base as (
    select count(distinct account_id) as total_accounts
    from {{ ref('dim_accounts') }}
),

daily_events as (
    select
        event_date as usage_date,

        count(*) as total_events,
        count(distinct account_id) as active_accounts,
        count(distinct user_id) as active_users,

        count(*) filter (where event_type = 'login') as login_events,
        count(*) filter (where event_type = 'account_created') as account_created_events,
        count(*) filter (where event_type = 'invite_user') as invite_user_events,
        count(*) filter (where event_type = 'create_project') as create_project_events,
        count(*) filter (where event_type = 'use_core_feature') as core_feature_events,
        count(*) filter (where event_type = 'export_report') as export_report_events,
        count(*) filter (where event_type = 'upgrade_prompt_viewed') as upgrade_prompt_views,
        count(*) filter (where event_type = 'billing_page_viewed') as billing_page_views,
        count(*) filter (where event_type = 'cancellation_started') as cancellation_started_events,

        count(distinct account_id) filter (
            where event_type in ('account_created', 'invite_user', 'create_project', 'use_core_feature')
        ) as activated_accounts,

        count(distinct account_id) filter (
            where event_type = 'use_core_feature'
        ) as core_feature_accounts,

        count(distinct account_id) filter (
            where event_type = 'export_report'
        ) as report_export_accounts,

        count(distinct account_id) filter (
            where event_type = 'cancellation_started'
        ) as cancellation_started_accounts
    from {{ ref('fact_product_events') }}
    group by 1
),

final as (
    select
        d.usage_date,

        coalesce(e.total_events, 0) as total_events,
        coalesce(e.active_accounts, 0) as active_accounts,
        greatest(a.total_accounts - coalesce(e.active_accounts, 0), 0) as inactive_accounts,
        coalesce(e.active_users, 0) as active_users,

        coalesce(e.login_events, 0) as login_events,
        coalesce(e.account_created_events, 0) as account_created_events,
        coalesce(e.invite_user_events, 0) as invite_user_events,
        coalesce(e.create_project_events, 0) as create_project_events,
        coalesce(e.core_feature_events, 0) as core_feature_events,
        coalesce(e.export_report_events, 0) as export_report_events,
        coalesce(e.upgrade_prompt_views, 0) as upgrade_prompt_views,
        coalesce(e.billing_page_views, 0) as billing_page_views,
        coalesce(e.cancellation_started_events, 0) as cancellation_started_events,

        coalesce(e.activated_accounts, 0) as activated_accounts,
        coalesce(e.core_feature_accounts, 0) as core_feature_accounts,
        coalesce(e.report_export_accounts, 0) as report_export_accounts,
        coalesce(e.cancellation_started_accounts, 0) as cancellation_started_accounts,

        round(
            coalesce(e.activated_accounts, 0)::numeric
            / nullif(a.total_accounts, 0),
            4
        ) as activation_rate,

        round(
            coalesce(e.core_feature_accounts, 0)::numeric
            / nullif(a.total_accounts, 0),
            4
        ) as core_feature_adoption_rate,

        round(
            coalesce(e.report_export_accounts, 0)::numeric
            / nullif(a.total_accounts, 0),
            4
        ) as report_export_adoption_rate,

        round(
            coalesce(e.cancellation_started_accounts, 0)::numeric
            / nullif(a.total_accounts, 0),
            4
        ) as cancellation_intent_rate,

        current_timestamp as created_at
    from date_spine d
    cross join account_base a
    left join daily_events e
        on d.usage_date = e.usage_date
)

select *
from final
