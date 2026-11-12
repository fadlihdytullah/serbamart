{% macro incremental_since(column) %}
    {%- if var('from_day', none) -%}
        (date '{{ var('from_day') }}' - interval {{ var('lookback_days') }} days)
    {%- else -%}
        (select max({{ column }}) - interval {{ var('lookback_days') }} days from {{ this }})
    {%- endif -%}
{% endmacro %}
