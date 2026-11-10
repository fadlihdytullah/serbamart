select
    sale_id,
    channel,
    sales_date as date_day,
    coalesce(branch_id, 'WEB') as branch_id,
    sku,
    qty,
    unit_price,
    revenue
from {{ ref('int_sales_lines') }}
