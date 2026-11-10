select
    'store' as channel,
    sales_date,
    branch_id,
    transaction_id as sale_id,
    sku,
    qty,
    unit_price,
    qty * unit_price as revenue
from {{ ref('stg_pos_sales') }}

union all

select
    'online' as channel,
    orders.order_date as sales_date,
    null as branch_id,
    lines.order_id as sale_id,
    lines.sku,
    lines.qty,
    lines.unit_price,
    lines.qty * lines.unit_price as revenue
from {{ ref('stg_online_order_lines') }} as lines
join {{ ref('stg_online_orders') }} as orders using (order_id)
where orders.status = 'paid'
