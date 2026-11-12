{{ config(
    location='../exports/fct_sales',
    format='parquet',
    options={'partition_by': 'date_day', 'overwrite': true}
) }}

select * from {{ ref('fct_sales') }}
