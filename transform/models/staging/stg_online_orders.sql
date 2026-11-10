select
    order_id,
    order_date,
    cast(payload ->> 'created_at' as timestamptz) as created_at,
    payload ->> 'customer_id' as customer_id,
    payload ->> 'city' as city,
    payload ->> 'status' as status
from {{ source('raw', 'online_orders') }}
