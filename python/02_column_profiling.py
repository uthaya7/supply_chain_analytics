import pandas as pd
import sys
from pathlib import Path


# File paths
project_root = Path(__file__).resolve().parent.parent
documentation_path = project_root / "documentation"
documentation_path.mkdir(
    parents=True,
    exist_ok=True
)

# Report path for column profiling summary
report_path = documentation_path / "02_column_profiling_summary.txt"


class Tee:

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


report_file = report_path.open(
    "w",
    encoding="utf-8"
)
sys.stdout = Tee(sys.stdout, report_file)

# ============================================================
# LOAD DATA
# ============================================================

file_path = project_root / "data" / "raw" / "DataCoSupplyChainDataset.csv"

df = pd.read_csv(
    file_path,
    encoding="latin1"
)

print("=" * 80)
print("SUPPLY CHAIN COLUMN PROFILING")
print("=" * 80)


# ============================================================
# PROFILE IMPORTANT CATEGORICAL COLUMNS
# ============================================================

columns_to_profile = [
    "Type",
    "Delivery Status",
    "Late_delivery_risk",
    "Customer Segment",
    "Market",
    "Shipping Mode",
    "Order Status",
    "Order Region",
    "Product Status",
    "Department Name",
    "Category Name"
]


for column in columns_to_profile:

    print("\n" + "=" * 80)
    print(f"COLUMN: {column}")
    print("=" * 80)

    print(
        df[column]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# NUMERICAL COLUMNS
# ============================================================

numeric_columns = [
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Benefit per order",
    "Sales per customer",
    "Order Item Discount",
    "Order Item Discount Rate",
    "Order Item Product Price",
    "Order Item Profit Ratio",
    "Order Item Quantity",
    "Sales",
    "Order Item Total",
    "Order Profit Per Order",
    "Product Price"
]


print("\n" + "=" * 80)
print("NUMERICAL COLUMN SUMMARY")
print("=" * 80)

print(
    df[numeric_columns]
    .describe()
    .T
    .to_string()
)


# ============================================================
# DATE COLUMNS
# ============================================================

date_columns = [
    "order date (DateOrders)",
    "shipping date (DateOrders)"
]


print("\n" + "=" * 80)
print("DATE RANGE")
print("=" * 80)

for column in date_columns:

    dates = pd.to_datetime(
        df[column],
        errors="coerce"
    )

    print(f"\n{column}")

    print(
        f"Minimum: {dates.min()}"
    )

    print(
        f"Maximum: {dates.max()}"
    )

    print(
        f"Invalid dates: {dates.isna().sum():,}"
    )


# ============================================================
# KEY ID COUNTS
# ============================================================

print("\n" + "=" * 80)
print("KEY ENTITY COUNTS")
print("=" * 80)

id_columns = [
    "Order Id",
    "Order Item Id",
    "Customer Id",
    "Product Card Id",
    "Product Category Id",
    "Department Id"
]

for column in id_columns:

    print(
        f"{column:30}: "
        f"{df[column].nunique():,}"
    )


print("\nProfiling completed.")

print(
    "Report saved to "
    f"{documentation_path / '02_column_profiling_summary.txt'}"
)

sys.stdout = sys.__stdout__
report_file.close()