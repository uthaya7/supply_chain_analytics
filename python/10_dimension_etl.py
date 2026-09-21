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
    / "10_dimension_etl_summary.txt"
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
print("SUPPLY CHAIN ANALYTICS - DIMENSION ETL")
print("=" * 80)

print("\nLoading clean dataset...")

df = pd.read_csv(file_path)

print(f"Source rows    : {len(df):,}")
print(f"Source columns : {len(df.columns):,}")


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


    # ========================================================
    # CHECK DIMENSION TABLES
    # ========================================================

    cursor = connection.cursor()

    dimension_tables = [
        "dim_customer",
        "dim_product",
        "dim_date",
        "dim_location",
        "dim_shipping"
    ]

    print("\n" + "=" * 80)
    print("DIMENSION TABLE STATUS")
    print("=" * 80)

    table_counts = {}

    for table in dimension_tables:

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM supply_chain.{table};
            """
        )

        count = cursor.fetchone()[0]

        table_counts[table] = count

        print(
            f"{table:<20} : {count:,} rows"
        )


    # ========================================================
    # SAFETY CHECK
    # ========================================================

    if any(
        count > 0
        for count in table_counts.values()
    ):

        raise RuntimeError(
            "One or more dimension tables already contain data. "
            "ETL stopped to prevent duplicate dimension loading."
        )


    # ========================================================
    # PREPARE DATA TYPES
    # ========================================================

    df["order_date_dateorders"] = pd.to_datetime(
        df["order_date_dateorders"],
        errors="coerce"
    )

    if df["order_date_dateorders"].isna().any():

        raise ValueError(
            "Invalid order dates detected during dimension ETL."
        )


    # ========================================================
    # 1. CUSTOMER DIMENSION
    # ========================================================

    print("\n" + "=" * 80)
    print("1. LOADING DIM_CUSTOMER")
    print("=" * 80)

    customer_columns = [
        "customer_id",
        "customer_segment",
        "customer_city",
        "customer_state",
        "customer_country"
    ]

    customers = (
        df[customer_columns]
        .drop_duplicates()
        .sort_values("customer_id")
    )

    print(
        f"Unique customers prepared: "
        f"{len(customers):,}"
    )

    customer_values = list(
        customers.itertuples(
            index=False,
            name=None
        )
    )

    execute_values(
        cursor,
        """
        INSERT INTO supply_chain.dim_customer (
            customer_id,
            customer_segment,
            customer_city,
            customer_state,
            customer_country
        )
        VALUES %s
        """,
        customer_values
    )

    print(
        f"Customers inserted: "
        f"{len(customer_values):,}"
    )


    # ========================================================
    # 2. PRODUCT DIMENSION
    # ========================================================

    print("\n" + "=" * 80)
    print("2. LOADING DIM_PRODUCT")
    print("=" * 80)

    product_columns = [
        "product_card_id",
        "product_name",
        "product_price",
        "product_status",
        "category_id",
        "category_name",
        "department_id",
        "department_name"
    ]

    products = (
        df[product_columns]
        .drop_duplicates(
            subset=["product_card_id"]
        )
        .sort_values("product_card_id")
    )

    products = products.rename(
        columns={
            "product_card_id": "product_id"
        }
    )

    print(
        f"Unique products prepared: "
        f"{len(products):,}"
    )

    product_values = list(
        products.itertuples(
            index=False,
            name=None
        )
    )

    execute_values(
        cursor,
        """
        INSERT INTO supply_chain.dim_product (
            product_id,
            product_name,
            product_price,
            product_status,
            category_id,
            category_name,
            department_id,
            department_name
        )
        VALUES %s
        """,
        product_values
    )

    print(
        f"Products inserted: "
        f"{len(product_values):,}"
    )


    # ========================================================
    # 3. DATE DIMENSION
    # ========================================================

    print("\n" + "=" * 80)
    print("3. LOADING DIM_DATE")
    print("=" * 80)

    # Convert timestamps to calendar dates.
    # Multiple orders can occur on the same calendar date,
    # so we normalize timestamps before removing duplicates.

    dates = (
        df["order_date_dateorders"]
        .dt.normalize()
        .drop_duplicates()
        .sort_values()
        .to_frame(name="full_date")
    )

    dates["date_id"] = (
        dates["full_date"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    dates["year"] = (
        dates["full_date"].dt.year
    )

    dates["quarter"] = (
        dates["full_date"].dt.quarter
    )

    dates["month"] = (
        dates["full_date"].dt.month
    )

    dates["month_name"] = (
        dates["full_date"].dt.month_name()
    )

    dates["week"] = (
        dates["full_date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    dates["day"] = (
        dates["full_date"].dt.day
    )

    dates["day_name"] = (
        dates["full_date"].dt.day_name()
    )

    dates = dates[
        [
            "date_id",
            "full_date",
            "year",
            "quarter",
            "month",
            "month_name",
            "week",
            "day",
            "day_name"
        ]
    ]

    print(
        f"Unique calendar dates prepared: "
        f"{len(dates):,}"
    )

    date_values = list(
        dates.itertuples(
            index=False,
            name=None
        )
    )

    execute_values(
        cursor,
        """
        INSERT INTO supply_chain.dim_date (
            date_id,
            full_date,
            year,
            quarter,
            month,
            month_name,
            week,
            day,
            day_name
        )
        VALUES %s
        """,
        date_values
    )

    print(
        f"Dates inserted: "
        f"{len(date_values):,}"
    )


    # ========================================================
    # 4. LOCATION DIMENSION
    # ========================================================

    print("\n" + "=" * 80)
    print("4. LOADING DIM_LOCATION")
    print("=" * 80)

    # Geographic identity consists of the five geographic 
    # attributes below.

    # Latitude and longitude are retained as descriptive
    # attributes and are NOT part of the location key.

    geographic_columns = [
        "market",
        "order_region",
        "order_country",
        "order_state",
        "order_city"
    ]

    location_columns = [
        *geographic_columns,
        "latitude",
        "longitude"
    ]


    # --------------------------------------------------------
    # Build one row per geographic location
    # --------------------------------------------------------

    locations = (
        df[location_columns]
        .sort_values(geographic_columns)
        .groupby(
            geographic_columns,
            as_index=False
        )
        .agg(
            latitude=("latitude", "min"),
            longitude=("longitude", "min")
        )
    )


    print(
        f"Unique geographic locations prepared: "
        f"{len(locations):,}"
    )


    # --------------------------------------------------------
    # Validate expected geographic grain
    # --------------------------------------------------------

    if locations[geographic_columns].duplicated().any():

        raise ValueError(
            "Duplicate geographic locations detected."
        )


    # --------------------------------------------------------
    # Prepare PostgreSQL values
    # --------------------------------------------------------

    location_values = list(
        locations.itertuples(
            index=False,
            name=None
        )
    )


    # --------------------------------------------------------
    # Insert locations
    # --------------------------------------------------------

    execute_values(
        cursor,
        """
        INSERT INTO supply_chain.dim_location (
            market,
            order_region,
            order_country,
            order_state,
            order_city,
            latitude,
            longitude
        )
        VALUES %s
        """,
        location_values
    )


    print(
        f"Locations inserted: "
        f"{len(location_values):,}"
    )

    # ========================================================
    # 5. SHIPPING DIMENSION
    # ========================================================

    print("\n" + "=" * 80)
    print("5. LOADING DIM_SHIPPING")
    print("=" * 80)

    shipping_modes = (
        df["shipping_mode"]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    print(
        f"Unique shipping modes prepared: "
        f"{len(shipping_modes):,}"
    )

    shipping_values = [
        (mode,)
        for mode in shipping_modes
    ]

    execute_values(
        cursor,
        """
        INSERT INTO supply_chain.dim_shipping (
            shipping_mode
        )
        VALUES %s
        """,
        shipping_values
    )

    print(
        f"Shipping modes inserted: "
        f"{len(shipping_values):,}"
    )


    # ========================================================
    # COMMIT DIMENSIONS
    # ========================================================

    connection.commit()

    print("\n" + "=" * 80)
    print("DIMENSION LOAD COMMITTED")
    print("=" * 80)

    print(
        "All five dimension loads committed successfully."
    )


    # ========================================================
    # DATABASE ROW COUNT VALIDATION
    # ========================================================

    print("\n" + "=" * 80)
    print("POST-LOAD DIMENSION VALIDATION")
    print("=" * 80)

    for table in dimension_tables:

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM supply_chain.{table};
            """
        )

        count = cursor.fetchone()[0]

        print(
            f"{table:<20} : {count:,} rows"
        )


    # ========================================================
    # DISPLAY SHIPPING MODES
    # ========================================================

    print("\n" + "=" * 80)
    print("SHIPPING MODE VALIDATION")
    print("=" * 80)

    cursor.execute(
        """
        SELECT shipping_id, shipping_mode
        FROM supply_chain.dim_shipping
        ORDER BY shipping_id;
        """
    )

    shipping_results = cursor.fetchall()

    for shipping_id, shipping_mode in shipping_results:

        print(
            f"{shipping_id} → {shipping_mode}"
        )


    # ========================================================
    # CLOSE
    # ========================================================

    cursor.close()
    connection.close()

    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)

    print(
        "Dimension ETL completed successfully."
    )

    print(
        f"\nReport saved to: {report_path}"
    )


except Exception as error:

    if connection is not None:

        connection.rollback()

    print("\n" + "=" * 80)
    print("DIMENSION ETL ERROR")
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
        "\nDimension ETL: FAILED"
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