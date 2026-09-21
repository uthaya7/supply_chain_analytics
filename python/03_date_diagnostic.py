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


file_path = project_root / "data" / "raw" / "DataCoSupplyChainDataset.csv"

# Report path for date diagnostic summary
report_path = documentation_path / "03_date_diagnostic_summary.txt"

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


df = pd.read_csv(
    file_path,
    encoding="latin1"
)

date_columns = [
    "order date (DateOrders)",
    "shipping date (DateOrders)"
]

for column in date_columns:

    print("\n" + "=" * 80)
    print(f"DATE DIAGNOSTIC: {column}")
    print("=" * 80)

    print("\nFirst 20 raw values:")

    print(
        df[column]
        .head(20)
        .to_string(index=False)
    )

    print("\nSample random values:")

    print(
        df[column]
        .sample(20, random_state=42)
        .to_string(index=False)
    )

print(
    "Report saved to "
    f"{documentation_path / '03_date_diagnostic_summary.txt'}"
)

sys.stdout = sys.__stdout__
report_file.close()