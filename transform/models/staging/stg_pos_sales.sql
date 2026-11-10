with sales as (
    select * from {{ source('raw', 'pos_sales') }}
),

branches as (
    select branch_id, timezone from {{ source('raw', 'branches') }}
),

typed as (
    select distinct
        sales.transaction_id,
        sales.branch_id,
        {{ local_timestamp('sales.sold_at', 'branches.timezone') }} as sold_at,
        sales.sku,
        cast(sales.qty as integer) as qty,
        {{ parse_rupiah('sales.unit_price') }} as unit_price,
        coalesce(sales.payment_method, 'unknown') as payment_method
    from sales
    join branches using (branch_id)
    where sales.qty is not null
)

select
    *,
    {{ business_date('sold_at') }} as sales_date
from typed
