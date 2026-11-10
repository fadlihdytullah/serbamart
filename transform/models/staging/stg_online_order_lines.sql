with orders as (
    select
        order_id,
        from_json(payload -> 'items', '[{"sku": "VARCHAR", "qty": "INTEGER", "unit_price": "INTEGER"}]') as items
    from {{ source('raw', 'online_orders') }}
)

select
    order_id,
    item.sku,
    item.qty,
    item.unit_price
from orders, unnest(items) as t(item)
