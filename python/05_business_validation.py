import sys
import pandas as pd
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

FILE_PATH = project_root / "data" / "processed" / "supply_chain_clean.csv"

# Report path for business validation summary
report_path = documentation_path / "business_validation_summary.txt"

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
# LOAD CLEAN DATA
# ============================================================

df = pd.read_csv(FILE_PATH)

print("=" * 80)
print("SUPPLY CHAIN BUSINESS DATA VALIDATION")
print("=" * 80)

print(f"\nRows    : {len(df):,}")
print(f"Columns : {len(df.columns):,}")


# ============================================================
# 1. SHIPPING DELAY VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("1. SHIPPING DELAY VALIDATION")
print("=" * 80)

print("\nShipping delay distribution:")

print(
    df["shipping_delay_days"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 2. SHIPPING PERFORMANCE
# ============================================================

print("\n" + "=" * 80)
print("2. SHIPPING PERFORMANCE")
print("=" * 80)

print(
    df["shipping_performance"]
    .value_counts(dropna=False)
)


# ============================================================
# 3. DELIVERY STATUS VS SHIPPING PERFORMANCE
# ============================================================

print("\n" + "=" * 80)
print("3. DELIVERY STATUS VS SHIPPING PERFORMANCE")
print("=" * 80)

cross_delivery = pd.crosstab(
    df["delivery_status"],
    df["shipping_performance"],
    margins=True
)

print(cross_delivery)


# ============================================================
# 4. LATE DELIVERY RISK VS DELIVERY STATUS
# ============================================================

print("\n" + "=" * 80)
print("4. LATE DELIVERY RISK VS DELIVERY STATUS")
print("=" * 80)

cross_risk = pd.crosstab(
    df["late_delivery_risk"],
    df["delivery_status"],
    margins=True
)

print(cross_risk)


# ============================================================
# 5. ORDER STATUS VS DELIVERY STATUS
# ============================================================

print("\n" + "=" * 80)
print("5. ORDER STATUS VS DELIVERY STATUS")
print("=" * 80)

cross_order = pd.crosstab(
    df["order_status"],
    df["delivery_status"],
    margins=True
)

print(cross_order)


# ============================================================
# 6. NEGATIVE PROFIT
# ============================================================

print("\n" + "=" * 80)
print("6. NEGATIVE PROFIT ANALYSIS")
print("=" * 80)

negative_profit = df[
    df["order_profit_per_order"] < 0
]

print(
    f"Negative-profit records: "
    f"{len(negative_profit):,}"
)

print(
    f"Negative-profit percentage: "
    f"{len(negative_profit) / len(df) * 100:.2f}%"
)

print(
    f"Total negative profit: "
    f"{negative_profit['order_profit_per_order'].sum():,.2f}"
)


# ============================================================
# 7. ZERO / NEGATIVE SALES
# ============================================================

print("\n" + "=" * 80)
print("7. SALES VALIDATION")
print("=" * 80)

print(
    "Zero sales:",
    (df["sales"] == 0).sum()
)

print(
    "Negative sales:",
    (df["sales"] < 0).sum()
)


# ============================================================
# 8. QUANTITY VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("8. QUANTITY VALIDATION")
print("=" * 80)

print(
    "Zero quantity:",
    (df["order_item_quantity"] == 0).sum()
)

print(
    "Negative quantity:",
    (df["order_item_quantity"] < 0).sum()
)


# ============================================================
# 9. DISCOUNT VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("9. DISCOUNT VALIDATION")
print("=" * 80)

print(
    "Discount < 0:",
    (df["order_item_discount"] < 0).sum()
)

print(
    "Discount rate < 0:",
    (df["order_item_discount_rate"] < 0).sum()
)

print(
    "Discount rate > 25%:",
    (df["order_item_discount_rate"] > 0.25).sum()
)


# ============================================================
# 10. DATE CONSISTENCY
# ============================================================

print("\n" + "=" * 80)
print("10. DATE CONSISTENCY")
print("=" * 80)

df["order_date_dateorders"] = pd.to_datetime(
    df["order_date_dateorders"],
    errors="coerce"
)

df["shipping_date_dateorders"] = pd.to_datetime(
    df["shipping_date_dateorders"],
    errors="coerce"
)

invalid_shipping_dates = (
    df["shipping_date_dateorders"]
    <
    df["order_date_dateorders"]
)

print(
    "Shipping before order:",
    invalid_shipping_dates.sum()
)


# ============================================================
# 11. SHIPPING DAYS VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("11. SHIPPING DAYS VALIDATION")
print("=" * 80)

print(
    "Negative actual shipping days:",
    (
        df["days_for_shipping_real"] < 0
    ).sum()
)

print(
    "Negative scheduled shipping days:",
    (
        df["days_for_shipment_scheduled"] < 0
    ).sum()
)


# ============================================================
# 12. ORDER / ORDER ITEM RELATIONSHIP
# ============================================================

print("\n" + "=" * 80)
print("12. ORDER / ORDER ITEM RELATIONSHIP")
print("=" * 80)

print(
    f"Unique Orders: "
    f"{df['order_id'].nunique():,}"
)

print(
    f"Unique Order Items: "
    f"{df['order_item_id'].nunique():,}"
)

items_per_order = (
    df.groupby("order_id")
    .size()
)

print(
    f"Average items per order: "
    f"{items_per_order.mean():.2f}"
)

print(
    f"Maximum items in one order: "
    f"{items_per_order.max():,}"
)


# ============================================================
# 13. SHIPPING PERFORMANCE BY MODE
# ============================================================

print("\n" + "=" * 80)
print("13. SHIPPING PERFORMANCE BY MODE")
print("=" * 80)

mode_analysis = (
    df.groupby("shipping_mode")
    .agg(
        Orders=("order_id", "nunique"),
        Order_Items=("order_item_id", "nunique"),
        Avg_Delay=("shipping_delay_days", "mean"),
        Late_Risk=("late_delivery_risk", "mean")
    )
    .sort_values(
        "Late_Risk",
        ascending=False
    )
)

mode_analysis["Late_Risk"] *= 100

print(
    mode_analysis.round(2)
)


# ============================================================
# 14. MARKET PERFORMANCE
# ============================================================

print("\n" + "=" * 80)
print("14. MARKET PERFORMANCE")
print("=" * 80)

market_analysis = (
    df.groupby("market")
    .agg(
        Orders=("order_id", "nunique"),
        Sales=("sales", "sum"),
        Profit=("order_profit_per_order", "sum"),
        Avg_Delay=("shipping_delay_days", "mean"),
        Late_Risk=("late_delivery_risk", "mean")
    )
    .sort_values(
        "Late_Risk",
        ascending=False
    )
)

market_analysis["Late_Risk"] *= 100

print(
    market_analysis.round(2)
)


print("\n" + "=" * 80)
print("BUSINESS VALIDATION COMPLETED")
print("=" * 80)

print(
    "Report saved to "
    f"{documentation_path / '05_business_validation_summary.txt'}"
)

sys.stdout = sys.__stdout__
report_file.close()