with sales as (
    select * from {{ source('raw', 'pos_sales') }}
),

branches as (
    select branch_id, timezone from {{ source('raw', 'branches') }}
)

select distinct
    sales.transaction_id,
    sales.branch_id,
    case
        when length(sales.sold_at) > 19 then cast(sales.sold_at as timestamptz)
        else timezone(branches.timezone, cast(sales.sold_at as timestamp))
    end as sold_at,
    sales.sku,
    cast(sales.qty as integer) as qty,
    cast(replace(replace(sales.unit_price, 'Rp', ''), '.', '') as integer) as unit_price,
    coalesce(sales.payment_method, 'unknown') as payment_method
from sales
join branches using (branch_id)
where sales.qty is not null
