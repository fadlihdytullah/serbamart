{% macro parse_rupiah(column) %}
    cast(replace(replace({{ column }}, 'Rp', ''), '.', '') as integer)
{% endmacro %}
