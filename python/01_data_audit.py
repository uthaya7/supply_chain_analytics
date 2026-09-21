import pandas as pd
import numpy as np
from pathlib import Path


# File paths
project_root = Path(__file__).resolve().parent.parent
documentation_path = project_root / "documentation"
documentation_path.mkdir(parents=True, exist_ok=True)

file_path = project_root / "data" / "raw" / "DataCoSupplyChainDataset.csv"

print("=" * 70)
print("SUPPLY CHAIN DATA AUDIT")
print("=" * 70)


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(
    file_path,
    encoding="latin1"
)

print("\nDataset loaded successfully!")


# ============================================================
# 3. BASIC DATASET INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("1. DATASET INFORMATION")
print("=" * 70)

print(f"Rows    : {df.shape[0]:,}")
print(f"Columns : {df.shape[1]:,}")

print("\nMemory Usage:")
print(f"{df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")


# ============================================================
# 4. COLUMN NAMES
# ============================================================

print("\n" + "=" * 70)
print("2. COLUMN NAMES")
print("=" * 70)

for i, column in enumerate(df.columns, start=1):
    print(f"{i:02d}. {column}")


# ============================================================
# 5. DATA TYPES
# ============================================================

print("\n" + "=" * 70)
print("3. DATA TYPES")
print("=" * 70)

print(df.dtypes)


# ============================================================
# 6. MISSING VALUES
# ============================================================

print("\n" + "=" * 70)
print("4. MISSING VALUES")
print("=" * 70)

missing = pd.DataFrame({
    "Missing_Count": df.isnull().sum(),
    "Missing_Percentage": (
        df.isnull().mean() * 100
    ).round(2)
})

missing = missing[
    missing["Missing_Count"] > 0
].sort_values(
    "Missing_Count",
    ascending=False
)

if missing.empty:
    print("No missing values found.")
else:
    print(missing)


# ============================================================
# 7. DUPLICATES
# ============================================================

print("\n" + "=" * 70)
print("5. DUPLICATE RECORDS")
print("=" * 70)

duplicate_count = df.duplicated().sum()

print(f"Duplicate rows: {duplicate_count:,}")


# ============================================================
# 8. UNIQUE VALUES
# ============================================================

print("\n" + "=" * 70)
print("6. UNIQUE VALUES")
print("=" * 70)

unique_summary = pd.DataFrame({
    "Column": df.columns,
    "Unique_Values": [
        df[column].nunique(dropna=False)
        for column in df.columns
    ]
})

print(unique_summary.to_string(index=False))


# ============================================================
# 9. NUMERICAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("7. NUMERICAL SUMMARY")
print("=" * 70)

print(
    df.describe(
        include=[np.number]
    ).T.to_string()
)


# ============================================================
# 10. DATE COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("8. POSSIBLE DATE COLUMNS")
print("=" * 70)

date_keywords = [
    "date",
    "day",
    "year",
    "month",
    "time"
]

possible_dates = [
    column
    for column in df.columns
    if any(
        keyword in column.lower()
        for keyword in date_keywords
    )
]

for column in possible_dates:
    print(column)


# ============================================================
# 11. CATEGORICAL COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("9. CATEGORICAL COLUMNS")
print("=" * 70)

categorical_columns = df.select_dtypes(
    include=["object"]
).columns

for column in categorical_columns:
    print(
        f"{column:40} "
        f"{df[column].nunique():>8,} unique values"
    )


# ============================================================
# 12. BASIC BUSINESS CHECKS
# ============================================================

print("\n" + "=" * 70)
print("10. BUSINESS SANITY CHECKS")
print("=" * 70)

checks = {}

if "Order Id" in df.columns:
    checks["Unique Orders"] = df["Order Id"].nunique()

if "Order Item Id" in df.columns:
    checks["Unique Order Items"] = df["Order Item Id"].nunique()

if "Customer Id" in df.columns:
    checks["Unique Customers"] = df["Customer Id"].nunique()

if "Product Card Id" in df.columns:
    checks["Unique Products"] = df["Product Card Id"].nunique()

if "Order Status" in df.columns:
    checks["Order Status Values"] = df["Order Status"].nunique()

if "Shipping Mode" in df.columns:
    checks["Shipping Modes"] = df["Shipping Mode"].nunique()

if "Market" in df.columns:
    checks["Markets"] = df["Market"].nunique()

for name, value in checks.items():
    print(f"{name:30}: {value}")


# ============================================================
# 13. SAVE AUDIT REPORT
# ============================================================

documentation_path = project_root / "documentation"

documentation_path.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    documentation_path / "01_data_audit_summary.txt",
    "w",
    encoding="utf-8"
) as file:

    file.write("SUPPLY CHAIN DATA AUDIT\n")
    file.write("=" * 70 + "\n\n")

    file.write(
        f"Rows: {df.shape[0]:,}\n"
    )

    file.write(
        f"Columns: {df.shape[1]:,}\n\n"
    )

    file.write("COLUMNS\n")
    file.write("-" * 70 + "\n")

    for i, column in enumerate(
        df.columns,
        start=1
    ):
        file.write(
            f"{i:02d}. {column}\n"
        )

    file.write("\nMISSING VALUES\n")
    file.write("-" * 70 + "\n")

    file.write(
        missing.to_string()
    )

    file.write("\n\nDUPLICATES\n")
    file.write("-" * 70 + "\n")

    file.write(
        f"Duplicate rows: {duplicate_count:,}\n"
    )

print("\nAudit completed successfully.")
print(
    "Report saved to "
    f"{documentation_path / '01_data_audit_summary.txt'}"
)