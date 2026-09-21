import sys
import pandas as pd
from pathlib import Path

# File paths
project_root = Path(__file__).resolve().parent.parent
file_path = project_root / "data" / "processed" / "supply_chain_clean.csv"

df = pd.read_csv(file_path)

# Report path for key relationship validation summary
documentation_path = project_root / "documentation"
documentation_path.mkdir(
    parents=True,
    exist_ok=True
)

report_path = documentation_path / "07_key_relationship_validation_summary.txt"

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


print("=" * 80)
print("SUPPLY CHAIN KEY RELATIONSHIP VALIDATION")
print("=" * 80)


# ============================================================
# 1. CUSTOMER ID VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("1. CUSTOMER ID vs ORDER CUSTOMER ID")
print("=" * 80)

customer_match = (
    df["customer_id"]
    ==
    df["order_customer_id"]
)

print(
    f"Matching rows: "
    f"{customer_match.sum():,}"
)

print(
    f"Non-matching rows: "
    f"{(~customer_match).sum():,}"
)

print(
    f"Match percentage: "
    f"{customer_match.mean() * 100:.2f}%"
)


# ============================================================
# 2. CATEGORY ID VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("2. CATEGORY ID vs PRODUCT CATEGORY ID")
print("=" * 80)

category_match = (
    df["category_id"]
    ==
    df["product_category_id"]
)

print(
    f"Matching rows: "
    f"{category_match.sum():,}"
)

print(
    f"Non-matching rows: "
    f"{(~category_match).sum():,}"
)

print(
    f"Match percentage: "
    f"{category_match.mean() * 100:.2f}%"
)


# ============================================================
# 3. PRODUCT CARD ID VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("3. PRODUCT CARD ID vs ORDER ITEM CARDPROD ID")
print("=" * 80)

product_match = (
    df["product_card_id"]
    ==
    df["order_item_cardprod_id"]
)

print(
    f"Matching rows: "
    f"{product_match.sum():,}"
)

print(
    f"Non-matching rows: "
    f"{(~product_match).sum():,}"
)

print(
    f"Match percentage: "
    f"{product_match.mean() * 100:.2f}%"
)


# ============================================================
# 4. UNIQUE CUSTOMER RELATIONSHIP
# ============================================================

print("\n" + "=" * 80)
print("4. CUSTOMER CARDINALITY")
print("=" * 80)

print(
    f"Unique customer_id: "
    f"{df['customer_id'].nunique():,}"
)

print(
    f"Unique order_customer_id: "
    f"{df['order_customer_id'].nunique():,}"
)


# ============================================================
# 5. PRODUCT CARDINALITY
# ============================================================

print("\n" + "=" * 80)
print("5. PRODUCT CARDINALITY")
print("=" * 80)

print(
    f"Unique product_card_id: "
    f"{df['product_card_id'].nunique():,}"
)

print(
    f"Unique order_item_cardprod_id: "
    f"{df['order_item_cardprod_id'].nunique():,}"
)

print(
    f"Unique product_name: "
    f"{df['product_name'].nunique():,}"
)


# ============================================================
# 6. CATEGORY CARDINALITY
# ============================================================

print("\n" + "=" * 80)
print("6. CATEGORY CARDINALITY")
print("=" * 80)

print(
    f"Unique category_id: "
    f"{df['category_id'].nunique():,}"
)

print(
    f"Unique product_category_id: "
    f"{df['product_category_id'].nunique():,}"
)

print(
    f"Unique category_name: "
    f"{df['category_name'].nunique():,}"
)


print("\n" + "=" * 80)
print("VALIDATION COMPLETED")
print("=" * 80)


print(
    "Report saved to "
    f"{documentation_path / '07_key_relationship_validation_summary.txt'}"
)

sys.stdout = sys.__stdout__
report_file.close()