{{ config(materialized='incremental', incremental_strategy='delete+insert', unique_key='sales_date') }}

select
    sales_date,
    channel,
    count(distinct sale_id) as sales,
    sum(qty) as units,
    sum(revenue) as revenue
from {{ ref('int_sales_lines') }}
{% if is_incremental() %}
where sales_date >= (select max(sales_date) from {{ this }})
{% endif %}
group by sales_date, channel
