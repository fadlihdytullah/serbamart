{% macro local_timestamp(column, timezone_column) %}
    case
        when length({{ column }}) > 19 then cast({{ column }} as timestamptz)
        else timezone({{ timezone_column }}, cast({{ column }} as timestamp))
    end
{% endmacro %}
