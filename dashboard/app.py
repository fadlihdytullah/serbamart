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

totals = query("""
    select
        cast(sum(revenue) as bigint) as revenue,
        count(distinct sale_id) as sales,
        max(date_day) as last_day
    from marts.fct_sales
""").iloc[0]

left, middle, right = st.columns(3)
left.metric("Revenue", rupiah(totals["revenue"]))
middle.metric("Sales", f"{totals['sales']:,}".replace(",", "."))
right.metric("Data through", str(totals["last_day"].date()))

daily = query("""
    select date_day, channel, cast(sum(revenue) as bigint) as revenue
    from marts.fct_sales
    group by all
    order by date_day
""")
st.subheader("Revenue per day")
st.line_chart(daily, x="date_day", y="revenue", color="channel")
