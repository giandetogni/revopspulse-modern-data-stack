{% test refund_not_greater_than_payment(model, refund_amount_column, payment_amount_column) %}

select *
from {{ model }}
where {{ refund_amount_column }} is not null
  and {{ payment_amount_column }} is not null
  and {{ refund_amount_column }} > {{ payment_amount_column }}

{% endtest %}
