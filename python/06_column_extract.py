import pandas as pd
import sys
from pathlib import Path


# File paths
project_root = Path(__file__).resolve().parent.parent
file_path = project_root / "data" / "processed" / "supply_chain_clean.csv"

# Report path for column summary
project_root = Path(__file__).resolve().parent.parent
documentation_path = project_root / "documentation"
documentation_path.mkdir(
    parents=True,
    exist_ok=True
)

df = pd.read_csv(file_path) 
report_path = documentation_path / "06_column_summary.txt"

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



for i, column in enumerate(df.columns, 1):
    print(f"{i:02d}. {column}")


print(
    "Report saved to "
    f"{documentation_path / '06_column_summary.txt'}"
)

sys.stdout = sys.__stdout__
report_file.close()