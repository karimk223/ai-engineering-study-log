import hashlib
from pathlib import Path

import pandas as pd


data_path = (
    Path(__file__).resolve().parent
    / "data"
    / "raw"
    / "customer_support.csv"
)

expected_sha256 = (
    "6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434"
)
actual_sha256 = hashlib.sha256(data_path.read_bytes()).hexdigest()

if actual_sha256 != expected_sha256:
    raise RuntimeError("Downloaded file does not match the recorded source.")

print("Dataset checksum verified.")

df = pd.read_csv(
    data_path,
    usecols=["instruction", "category"],
    dtype="string",
)

print("\nTotal rows:", len(df))
print("\nAll category counts:")
print(df["category"].value_counts().sort_index())

print("\nTwo examples per category:")
print(df.groupby("category").head(2).to_string(index=False))
