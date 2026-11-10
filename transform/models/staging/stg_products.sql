select
    sku,
    name,
    category,
    cast(unit_price as integer) as unit_price,
    cast(updated_on as date) as updated_on
from {{ source('raw', 'products') }}
