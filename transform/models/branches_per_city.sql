select city, count(*) as branches
from raw.branches
group by city
order by branches desc, city
