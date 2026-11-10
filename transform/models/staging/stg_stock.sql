select
    cast(parse_filename(_source_file, true) as date) as stock_date,
    branch_id,
    sku,
    cast(on_hand as integer) as on_hand
from {{ source('raw', 'stock') }}
