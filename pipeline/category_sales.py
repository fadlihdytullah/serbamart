import duckdb
import pandas as pd

sales = duckdb.sql("select sku, qty, unit_price from 'output/pos_sales.parquet'").df()
products = pd.read_csv("data/products.csv")

sales["revenue"] = sales["qty"] * sales["unit_price"]
with_category = sales.merge(products[["sku", "category"]], on="sku", how="left")

by_category = (
    with_category.groupby("category")
    .agg(units=("qty", "sum"), revenue=("revenue", "sum"))
    .sort_values("revenue", ascending=False)
)
by_category["share"] = (by_category["revenue"] / by_category["revenue"].sum() * 100).round(1)

print(by_category)
