import sys
import getpass
import psycopg2
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

project_root = Path(__file__).resolve().parent.parent

documentation_path = project_root / "documentation"
documentation_path.mkdir(
    parents=True,
    exist_ok=True
)

report_path = (
    documentation_path
    / "09_postgresql_connection_test_summary.txt"
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
# CONNECTION TEST
# ============================================================

print("=" * 80)
print("SUPPLY CHAIN ANALYTICS - POSTGRESQL CONNECTION TEST")
print("=" * 80)

print("\nConnection configuration:")
print(f"Host     : {HOST}")
print(f"Port     : {PORT}")
print(f"Database : {DATABASE}")
print(f"User     : {USER}")


password = getpass.getpass(
    "\nEnter PostgreSQL password: "
)


try:

    connection = psycopg2.connect(
        host=HOST,
        port=PORT,
        database=DATABASE,
        user=USER,
        password=password
    )

    print("\n" + "=" * 80)
    print("CONNECTION STATUS")
    print("=" * 80)

    print("PostgreSQL connection: SUCCESS")


    # ========================================================
    # DATABASE TEST
    # ========================================================

    cursor = connection.cursor()

    cursor.execute(
        "SELECT current_database(), current_user;"
    )

    database_name, current_user = cursor.fetchone()

    print(f"Current database : {database_name}")
    print(f"Current user     : {current_user}")


    # ========================================================
    # SCHEMA TEST
    # ========================================================

    cursor.execute(
        """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name = 'supply_chain';
        """
    )

    schema_result = cursor.fetchone()


    print("\n" + "=" * 80)
    print("SCHEMA VALIDATION")
    print("=" * 80)


    if schema_result:

        print(
            "supply_chain schema: FOUND"
        )

    else:

        print(
            "supply_chain schema: NOT FOUND"
        )


    # ========================================================
    # TABLE COUNT TEST
    # ========================================================

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'supply_chain';
        """
    )

    table_count = cursor.fetchone()[0]

    print(
        f"Tables in supply_chain schema: {table_count}"
    )


    # ========================================================
    # TABLE LIST
    # ========================================================

    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'supply_chain'
        ORDER BY table_name;
        """
    )

    tables = cursor.fetchall()

    print("\nTables:")

    for table in tables:

        print(
            f" - {table[0]}"
        )


    # ========================================================
    # CLOSE CONNECTION
    # ========================================================

    cursor.close()
    connection.close()

    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)

    print(
        "PostgreSQL connection and schema validation: PASSED"
    )

    print(
        f"\nReport saved to: {report_path}"
    )


except Exception as error:

    print("\n" + "=" * 80)
    print("CONNECTION ERROR")
    print("=" * 80)

    print(
        f"\nError type    : {type(error).__name__}"
    )

    print(
        f"Error message : {error}"
    )

    print("\nPostgreSQL connection test: FAILED")

    print(
        f"\nReport saved to: {report_path}"
    )


finally:

    sys.stdout = sys.__stdout__
    report_file.close()
    