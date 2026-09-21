import sys
import pandas as pd
from pathlib import Path

# File paths
project_root = Path(__file__).resolve().parent.parent
file_path = project_root / "data" / "processed" / "supply_chain_clean.csv"

df = pd.read_csv(file_path)


# Report path for category validation summary

documentation_path = project_root / "documentation"
documentation_path.mkdir(
    parents=True,
    exist_ok=True
)
report_path = documentation_path / "08_category_validation_summary.txt"

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
print("CATEGORY ID vs CATEGORY NAME VALIDATION")
print("=" * 80)

# ============================================================
# 1. CATEGORY ID → CATEGORY NAME MAPPING
# ============================================================

category_mapping = (
    df[
        ["category_id", "category_name"]
    ]
    .drop_duplicates()
    .sort_values("category_id")
)

print("\nCategory ID → Category Name:")
print(category_mapping.to_string(index=False))


# ============================================================
# 2. CHECK WHETHER ONE ID HAS MULTIPLE NAMES
# ============================================================

id_name_counts = (
    df.groupby("category_id")["category_name"]
    .nunique()
)

print("\n" + "=" * 80)
print("1. CATEGORY IDs WITH MULTIPLE NAMES")
print("=" * 80)

multiple_names = id_name_counts[id_name_counts > 1]

print(
    f"Category IDs with multiple names: "
    f"{len(multiple_names)}"
)

if len(multiple_names) > 0:
    print(multiple_names)


# ============================================================
# 3. CHECK WHETHER ONE NAME HAS MULTIPLE IDs
# ============================================================

name_id_counts = (
    df.groupby("category_name")["category_id"]
    .nunique()
)

print("\n" + "=" * 80)
print("2. CATEGORY NAMES WITH MULTIPLE IDs")
print("=" * 80)

multiple_ids = name_id_counts[name_id_counts > 1]

print(
    f"Category names with multiple IDs: "
    f"{len(multiple_ids)}"
)

if len(multiple_ids) > 0:
    print(multiple_ids)


# ============================================================
# 4. FULL DUPLICATE MAPPING CHECK
# ============================================================

print("\n" + "=" * 80)
print("3. DUPLICATE CATEGORY NAME MAPPINGS")
print("=" * 80)

duplicate_names = (
    category_mapping
    .groupby("category_name")
    .filter(
        lambda x: x["category_id"].nunique() > 1
    )
)

print(duplicate_names.to_string(index=False))


# ============================================================
# 5. SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("CATEGORY VALIDATION SUMMARY")
print("=" * 80)

print(
    f"Unique category IDs   : "
    f"{df['category_id'].nunique():,}"
)

print(
    f"Unique category names : "
    f"{df['category_name'].nunique():,}"
)

print(
    f"ID → multiple names   : "
    f"{len(multiple_names)}"
)

print(
    f"Name → multiple IDs   : "
    f"{len(multiple_ids)}"
)

print("\nVALIDATION COMPLETED")



print(
    "Report saved to "
    f"{documentation_path / '08_category_validation_summary.txt'}"
)

sys.stdout = sys.__stdout__
report_file.close()