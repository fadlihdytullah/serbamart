import duckdb
import streamlit as st

WAREHOUSE = "warehouse/serbamart.duckdb"

st.set_page_config(page_title="Serbamart sales", layout="wide")


@st.cache_data(ttl=600)
def query(sql, params=None):
    with duckdb.connect(WAREHOUSE, read_only=True) as con:
        return con.execute(sql, params or []).df()


def rupiah(amount):
    return f"Rp{int(amount):,}".replace(",", ".")


st.title("Serbamart sales")

bounds = query("select min(date_day) as first_day, max(date_day) as last_day from marts.fct_sales").iloc[0]
cities = query("select distinct city from marts.dim_branch order by city")["city"].tolist()

with st.sidebar:
    days = st.date_input(
        "Days",
        value=(bounds["last_day"].date().replace(day=1), bounds["last_day"].date()),
        min_value=bounds["first_day"].date(),
        max_value=bounds["last_day"].date(),
    )
    chosen = st.multiselect("Cities", cities, default=cities)

if len(days) < 2:
    st.info("Pick the last day of the range.")
    st.stop()
start, end = days

filters = """
    from marts.fct_sales as f
    join marts.dim_branch as b using (branch_id)
    join marts.dim_product as p using (product_key)
    where f.date_day between ? and ? and list_contains(?, b.city)
"""
params = [start, end, chosen]

totals = query(f"""
    select cast(coalesce(sum(f.revenue), 0) as bigint) as revenue, count(distinct f.sale_id) as sales
    {filters}
""", params).iloc[0]

left, right = st.columns(2)
left.metric("Revenue", rupiah(totals["revenue"]))
right.metric("Sales", f"{totals['sales']:,}".replace(",", "."))

daily = query(f"""
    select f.date_day, f.channel, cast(sum(f.revenue) as bigint) as revenue
    {filters}
    group by all
    order by f.date_day
""", params)
st.subheader("Revenue per day")
st.line_chart(daily, x="date_day", y="revenue", color="channel")

left, right = st.columns(2)

categories = query(f"""
    select p.category, cast(sum(f.revenue) as bigint) as revenue
    {filters}
    group by all
    order by revenue desc
""", params)
left.subheader("Revenue per category")
left.bar_chart(categories, x="category", y="revenue", horizontal=True, sort="-revenue")

top = query(f"""
    select p.name, cast(sum(f.qty) as bigint) as units, cast(sum(f.revenue) as bigint) as revenue
    {filters}
    group by all
    order by units desc
    limit 10
""", params)
right.subheader("Top products")
right.dataframe(top, hide_index=True)
