{% test valid_subscription_period(model, start_column, end_column) %}

select *
from {{ model }}
where {{ end_column }} is not null
  and {{ start_column }} is not null
  and {{ end_column }} < {{ start_column }}

{% endtest %}
