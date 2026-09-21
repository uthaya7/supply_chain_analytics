import sys

import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

# File paths
project_root = Path(__file__).resolve().parent.parent
documentation_path = project_root / "documentation"
documentation_path.mkdir(
    parents=True,
    exist_ok=True
)


RAW_FILE = project_root / "data" / "raw" / "DataCoSupplyChainDataset.csv"

PROCESSED_DIR = Path(
    project_root / "data" / "processed"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "supply_chain_clean.csv"
)

# Report path for data cleaning summary
report_path = documentation_path / "04_data_cleaning_summary.txt"

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
# 1. LOAD RAW DATA
# ============================================================

print("=" * 80)
print("SUPPLY CHAIN DATA CLEANING PIPELINE")
print("=" * 80)

print("\n[1/9] Loading raw dataset...")

df = pd.read_csv(
    RAW_FILE,
    encoding="latin1"
)

print(
    f"Loaded {len(df):,} rows "
    f"and {len(df.columns)} columns."
)


# ============================================================
# 2. STANDARDIZE COLUMN NAMES
# ============================================================

print("\n[2/9] Standardizing column names...")

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "", regex=False)
    .str.replace(")", "", regex=False)
    .str.replace("-", "_")
)

print("Column names standardized.")


# ============================================================
# 3. REMOVE PII / UNNECESSARY COLUMNS
# ============================================================

print("\n[3/9] Removing unnecessary / sensitive columns...")

columns_to_remove = [
    "customer_email",
    "customer_password",
    "customer_fname",
    "customer_lname",
    "customer_street",
    "customer_zipcode",
    "order_zipcode",
    "product_description",
    "product_image"
]

existing_columns = [
    column
    for column in columns_to_remove
    if column in df.columns
]

df.drop(
    columns=existing_columns,
    inplace=True
)

print("Removed columns:")

for column in existing_columns:
    print(f"  - {column}")


# ============================================================
# 4. CLEAN DATETIME COLUMNS
# ============================================================

print("\n[4/9] Cleaning date fields...")

date_columns = [
    "order_date_dateorders",
    "shipping_date_dateorders"
]

for column in date_columns:

    if column in df.columns:

        # Remove leading/trailing spaces
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

        # Convert mixed date formats
        df[column] = pd.to_datetime(
            df[column],
            format="mixed",
            errors="coerce"
        )

        print(
            f"{column}: "
            f"{df[column].isna().sum():,} invalid values"
        )


# ============================================================
# 5. HANDLE MISSING VALUES
# ============================================================

print("\n[5/9] Handling missing values...")

# Numeric fields
numeric_fill_zero = [
    "customer_zipcode",
    "order_zipcode"
]

for column in numeric_fill_zero:

    if column in df.columns:

        df[column] = df[column].fillna(0)


# Categorical fields
categorical_columns = df.select_dtypes(
    include=["object", "string"]
).columns

for column in categorical_columns:

    df[column] = (
        df[column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

print("Missing-value treatment completed.")


# ============================================================
# 6. NUMERIC DATA TYPES
# ============================================================

print("\n[6/9] Standardizing numeric fields...")

numeric_columns = [
    "days_for_shipping_real",
    "days_for_shipment_scheduled",
    "benefit_per_order",
    "sales_per_customer",
    "order_item_discount",
    "order_item_discount_rate",
    "order_item_product_price",
    "order_item_profit_ratio",
    "order_item_quantity",
    "sales",
    "order_item_total",
    "order_profit_per_order",
    "product_price"
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# ============================================================
# 7. BUSINESS FEATURE ENGINEERING
# ============================================================

print("\n[7/9] Creating analytical features...")


# Shipping delay
df["shipping_delay_days"] = (
    df["days_for_shipping_real"]
    -
    df["days_for_shipment_scheduled"]
)


# Delivery performance category
df["shipping_performance"] = np.select(
    [
        df["shipping_delay_days"] > 0,
        df["shipping_delay_days"] == 0,
        df["shipping_delay_days"] < 0
    ],
    [
        "Delayed",
        "On Schedule",
        "Ahead of Schedule"
    ],
    default="Unknown"
)


# Profit margin
df["profit_margin"] = np.where(
    df["sales"] != 0,
    df["order_profit_per_order"] /
    df["sales"],
    0
)


# Discount percentage
df["discount_percentage"] = (
    df["order_item_discount_rate"] * 100
)


print("Created:")
print("  - shipping_delay_days")
print("  - shipping_performance")
print("  - profit_margin")
print("  - discount_percentage")


# ============================================================
# 8. DATA QUALITY VALIDATION
# ============================================================

print("\n[8/9] Running data-quality checks...")

print(
    f"Rows after cleaning: "
    f"{len(df):,}"
)

print(
    f"Columns after cleaning: "
    f"{len(df.columns)}"
)

print(
    f"Duplicate rows: "
    f"{df.duplicated().sum():,}"
)

print(
    f"Missing values: "
    f"{df.isna().sum().sum():,}"
)


# ============================================================
# 9. EXPORT
# ============================================================

print("\n[9/9] Saving cleaned dataset...")

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nClean dataset saved to:\n"
    f"{OUTPUT_FILE}"
)

print("\n" + "=" * 80)
print("CLEANING PIPELINE COMPLETED")
print("=" * 80)


print(
    "Report saved to "
    f"{documentation_path / '04_data_cleaning_summary.txt'}"
)

sys.stdout = sys.__stdout__
report_file.close()