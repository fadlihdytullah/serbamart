{% macro business_date(column) %}
    cast(timezone('{{ var("business_timezone") }}', {{ column }}) as date)
{% endmacro %}
