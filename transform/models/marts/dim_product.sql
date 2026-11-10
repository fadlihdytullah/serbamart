select
    dbt_scd_id as product_key,
    sku,
    name,
    category,
    unit_price,
    dbt_valid_from as valid_from,
    coalesce(dbt_valid_to, date '9999-12-31') as valid_to,
    dbt_valid_to is null as is_current
from {{ ref('products_snapshot') }}
