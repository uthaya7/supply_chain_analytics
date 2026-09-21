import sys
import getpass
import psycopg2
import pandas as pd

from pathlib import Path
from psycopg2.extras import execute_values


# ============================================================
# PROJECT PATHS
# ============================================================

project_root = Path(__file__).resolve().parent.parent

file_path = (
    project_root
    / "data"
    / "processed"
    / "supply_chain_clean.csv"
)

documentation_path = project_root / "documentation"

documentation_path.mkdir(
    parents=True,
    exist_ok=True
)

report_path = (
    documentation_path
    / "11_fact_etl_summary.txt"
)


# ============================================================
# REPORT OUTPUT
# ============================================================

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

sys.stdout = Tee(
    sys.stdout,
    report_file
)


# ============================================================
# POSTGRESQL CONFIGURATION
# ============================================================

HOST = "localhost"
PORT = 5432
DATABASE = "supply_chain_analytics"
USER = "postgres"


# ============================================================
# LOAD CLEAN DATA
# ============================================================

print("=" * 80)
print("SUPPLY CHAIN ANALYTICS - FACT ETL")
print("=" * 80)

print("\nLoading clean dataset...")

df = pd.read_csv(file_path)

print(f"Source rows    : {len(df):,}")
print(f"Source columns : {len(df.columns):,}")


# ============================================================
# BASIC SOURCE VALIDATION
# ============================================================

if len(df) != 180_519:

    raise ValueError(
        f"Unexpected source row count: {len(df):,}. "
        "Expected 180,519."
    )


if df["order_item_id"].duplicated().any():

    duplicate_count = (
        df["order_item_id"].duplicated().sum()
    )

    raise ValueError(
        f"Duplicate order_item_id values detected: "
        f"{duplicate_count:,}"
    )


# ============================================================
# DATABASE CONNECTION
# ============================================================

password = getpass.getpass(
    "\nEnter PostgreSQL password: "
)

connection = None


try:

    connection = psycopg2.connect(
        host=HOST,
        port=PORT,
        database=DATABASE,
        user=USER,
        password=password
    )

    print("\nPostgreSQL connection: SUCCESS")

    cursor = connection.cursor()


    # ========================================================
    # FACT TABLE SAFETY CHECK
    # ========================================================

    print("\n" + "=" * 80)
    print("FACT TABLE STATUS")
    print("=" * 80)

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM supply_chain.fact_order_items;
        """
    )

    existing_fact_rows = cursor.fetchone()[0]

    print(
        f"Existing fact rows: "
        f"{existing_fact_rows:,}"
    )

    if existing_fact_rows > 0:

        raise RuntimeError(
            "fact_order_items already contains data. "
            "ETL stopped to prevent duplicate loading."
        )


    # ========================================================
    # LOAD DIMENSION LOOKUPS
    # ========================================================

    print("\n" + "=" * 80)
    print("LOADING DIMENSION LOOKUPS")
    print("=" * 80)


    # --------------------------------------------------------
    # CUSTOMER LOOKUP
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT customer_id
        FROM supply_chain.dim_customer;
        """
    )

    customer_ids = {
        row[0]
        for row in cursor.fetchall()
    }

    print(
        f"Customer keys loaded : "
        f"{len(customer_ids):,}"
    )


    # --------------------------------------------------------
    # PRODUCT LOOKUP
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT product_id
        FROM supply_chain.dim_product;
        """
    )

    product_ids = {
        row[0]
        for row in cursor.fetchall()
    }

    print(
        f"Product keys loaded  : "
        f"{len(product_ids):,}"
    )


    # --------------------------------------------------------
    # DATE LOOKUP
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT date_id, full_date
        FROM supply_chain.dim_date;
        """
    )

    date_lookup = {
        pd.Timestamp(full_date).date(): date_id
        for date_id, full_date in cursor.fetchall()
    }

    print(
        f"Date keys loaded     : "
        f"{len(date_lookup):,}"
    )


    # --------------------------------------------------------
    # LOCATION LOOKUP
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            location_id,
            market,
            order_region,
            order_country,
            order_state,
            order_city
        FROM supply_chain.dim_location;
        """
    )

    location_lookup = {}

    for row in cursor.fetchall():

        (
            location_id,
            market,
            order_region,
            order_country,
            order_state,
            order_city
        ) = row

        key = (
            market,
            order_region,
            order_country,
            order_state,
            order_city
        )

        location_lookup[key] = location_id

    print(
        f"Location keys loaded : "
        f"{len(location_lookup):,}"
    )

    # --------------------------------------------------------
    # SHIPPING LOOKUP
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT shipping_id, shipping_mode
        FROM supply_chain.dim_shipping;
        """
    )

    shipping_lookup = {
        shipping_mode: shipping_id
        for shipping_id, shipping_mode
        in cursor.fetchall()
    }

    print(
        f"Shipping keys loaded : "
        f"{len(shipping_lookup):,}"
    )


    # ========================================================
    # PREPARE DATE VALUES
    # ========================================================

    print("\n" + "=" * 80)
    print("PREPARING FACT FOREIGN KEYS")
    print("=" * 80)

    df["order_date_dateorders"] = pd.to_datetime(
        df["order_date_dateorders"],
        errors="coerce"
    )

    if df["order_date_dateorders"].isna().any():

        invalid_dates = (
            df["order_date_dateorders"].isna().sum()
        )

        raise ValueError(
            f"Invalid order dates found: "
            f"{invalid_dates:,}"
        )


    df["fact_date"] = (
        df["order_date_dateorders"]
        .dt.date
    )

    df["date_id"] = (
        df["fact_date"]
        .map(date_lookup)
    )


    # ========================================================
    # CUSTOMER KEY VALIDATION
    # ========================================================

    missing_customers = (
        ~df["customer_id"].isin(customer_ids)
    )

    print(
        f"Missing customer keys: "
        f"{missing_customers.sum():,}"
    )

    if missing_customers.any():

        raise ValueError(
            "One or more customer IDs do not exist "
            "in dim_customer."
        )


    # ========================================================
    # PRODUCT KEY VALIDATION
    # ========================================================

    df["product_id"] = (
        df["product_card_id"]
    )

    missing_products = (
        ~df["product_id"].isin(product_ids)
    )

    print(
        f"Missing product keys : "
        f"{missing_products.sum():,}"
    )

    if missing_products.any():

        raise ValueError(
            "One or more product IDs do not exist "
            "in dim_product."
        )


    # ========================================================
    # DATE KEY VALIDATION
    # ========================================================

    missing_dates = df["date_id"].isna()

    print(
        f"Missing date keys    : "
        f"{missing_dates.sum():,}"
    )

    if missing_dates.any():

        raise ValueError(
            "One or more order dates do not exist "
            "in dim_date."
        )


    # ========================================================
    # SHIPPING KEY VALIDATION
    # ========================================================

    df["shipping_id"] = (
        df["shipping_mode"]
        .map(shipping_lookup)
    )

    missing_shipping = (
        df["shipping_id"].isna()
    )

    print(
        f"Missing shipping keys: "
        f"{missing_shipping.sum():,}"
    )

    if missing_shipping.any():

        raise ValueError(
            "One or more shipping modes do not exist "
            "in dim_shipping."
        )


    # ========================================================
    # LOCATION KEY VALIDATION
    # ========================================================

    location_keys = list(
        zip(
            df["market"],
            df["order_region"],
            df["order_country"],
            df["order_state"],
            df["order_city"]
        )
    )

    df["location_id"] = [
        location_lookup.get(key)
        for key in location_keys
    ]

    missing_locations = (
        df["location_id"].isna()
    )

    print(
        f"Missing location keys: "
        f"{missing_locations.sum():,}"
    )

    if missing_locations.any():

        raise ValueError(
            "One or more location combinations do not "
            "exist in dim_location."
        )


    # ========================================================
    # FOREIGN KEY SUMMARY
    # ========================================================

    print("\nForeign-key resolution:")

    print(
        "Customer : "
        "100% resolved"
    )

    print(
        "Product  : "
        "100% resolved"
    )

    print(
        "Date     : "
        "100% resolved"
    )

    print(
        "Location : "
        "100% resolved"
    )

    print(
        "Shipping : "
        "100% resolved"
    )


    # ========================================================
    # PREPARE FACT DATA
    # ========================================================

    print("\n" + "=" * 80)
    print("PREPARING FACT TABLE")
    print("=" * 80)


    fact_columns = [
        "order_item_id",
        "order_id",

        "customer_id",
        "product_id",
        "date_id",
        "location_id",
        "shipping_id",

        "days_for_shipping_real",
        "days_for_shipment_scheduled",
        "shipping_delay_days",

        "order_item_quantity",

        "benefit_per_order",
        "sales_per_customer",
        "order_item_discount",
        "order_item_discount_rate",
        "order_item_product_price",
        "order_item_profit_ratio",

        "sales",
        "order_item_total",
        "order_profit_per_order",
        "profit_margin",
        "discount_percentage",

        "delivery_status",
        "late_delivery_risk",
        "order_status",
        "shipping_performance",
        "type"
    ]


    missing_columns = [
        column
        for column in fact_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing fact columns: "
            + ", ".join(missing_columns)
        )


    fact_df = df[
        fact_columns
    ].copy()


    print(
        f"Fact rows prepared: "
        f"{len(fact_df):,}"
    )


    # ========================================================
    # NULL VALIDATION
    # ========================================================

    print("\n" + "=" * 80)
    print("FACT DATA VALIDATION")
    print("=" * 80)

    required_fk_columns = [
        "customer_id",
        "product_id",
        "date_id",
        "location_id",
        "shipping_id"
    ]

    for column in required_fk_columns:

        null_count = (
            fact_df[column]
            .isna()
            .sum()
        )

        print(
            f"{column:<15}: "
            f"{null_count:,} NULL"
        )

        if null_count > 0:

            raise ValueError(
                f"NULL foreign keys detected in {column}."
            )


    # ========================================================
    # ORDER ITEM DUPLICATE VALIDATION
    # ========================================================

    duplicate_fact_ids = (
        fact_df["order_item_id"]
        .duplicated()
        .sum()
    )

    print(
        f"\nDuplicate order_item_id: "
        f"{duplicate_fact_ids:,}"
    )

    if duplicate_fact_ids > 0:

        raise ValueError(
            "Duplicate order_item_id values detected."
        )


    # ========================================================
    # INSERT FACT DATA
    # ========================================================

    print("\n" + "=" * 80)
    print("INSERTING FACT ORDER ITEMS")
    print("=" * 80)

    fact_values = list(
        fact_df.itertuples(
            index=False,
            name=None
        )
    )

    print(
        f"Rows ready for insertion: "
        f"{len(fact_values):,}"
    )


    execute_values(
        cursor,
        """
        INSERT INTO supply_chain.fact_order_items (
            order_item_id,
            order_id,
            customer_id,
            product_id,
            date_id,
            location_id,
            shipping_id,
            days_for_shipping_real,
            days_for_shipment_scheduled,
            shipping_delay_days,
            order_item_quantity,
            benefit_per_order,
            sales_per_customer,
            order_item_discount,
            order_item_discount_rate,
            order_item_product_price,
            order_item_profit_ratio,
            sales,
            order_item_total,
            order_profit_per_order,
            profit_margin,
            discount_percentage,
            delivery_status,
            late_delivery_risk,
            order_status,
            shipping_performance,
            type
        )
        VALUES %s
        """,
        fact_values,
        page_size=5000
    )


    # ========================================================
    # FACT ROW COUNT BEFORE COMMIT
    # ========================================================

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM supply_chain.fact_order_items;
        """
    )

    fact_count = cursor.fetchone()[0]

    print(
        f"\nDatabase fact rows: "
        f"{fact_count:,}"
    )


    if fact_count != len(df):

        raise ValueError(
            f"Fact row count mismatch. "
            f"Database={fact_count:,}, "
            f"Source={len(df):,}"
        )


    # ========================================================
    # COMMIT
    # ========================================================

    connection.commit()

    print("\n" + "=" * 80)
    print("FACT ETL COMMITTED")
    print("=" * 80)

    print(
        "All 180,519 fact records committed successfully."
    )


    # ========================================================
    # POST-COMMIT VALIDATION
    # ========================================================

    print("\n" + "=" * 80)
    print("POST-LOAD FACT VALIDATION")
    print("=" * 80)


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM supply_chain.fact_order_items;
        """
    )

    final_fact_count = cursor.fetchone()[0]

    print(
        f"Final fact rows: "
        f"{final_fact_count:,}"
    )


    cursor.execute(
        """
        SELECT COUNT(DISTINCT order_item_id)
        FROM supply_chain.fact_order_items;
        """
    )

    unique_fact_ids = cursor.fetchone()[0]

    print(
        f"Unique order_item_id: "
        f"{unique_fact_ids:,}"
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)

    print(
        "Fact ETL completed successfully."
    )

    print(
        f"\nReport saved to: {report_path}"
    )


except Exception as error:

    if connection is not None:

        connection.rollback()

    print("\n" + "=" * 80)
    print("FACT ETL ERROR")
    print("=" * 80)

    print(
        f"\nError type    : {type(error).__name__}"
    )

    print(
        f"Error message : {error}"
    )

    print(
        "\nTransaction rolled back."
    )

    print(
        "\nFact ETL: FAILED"
    )

    print(
        f"\nReport saved to: {report_path}"
    )


finally:

    if connection is not None:

        try:
            connection.close()
        except Exception:
            pass

    sys.stdout = sys.__stdout__
    report_file.close()