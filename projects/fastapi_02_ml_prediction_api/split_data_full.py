from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


processed_dir = (
    Path(__file__).resolve().parent / "data" / "processed" / "full"
)
df = pd.read_csv(processed_dir / "support_tickets.csv", dtype="string")

# Keep 70% for training and set aside 30%.
train, remainder = train_test_split(
    df,
    test_size=0.30,
    random_state=42,
    stratify=df["category"],
)

# Divide that remaining 30% equally.
validation, test = train_test_split(
    remainder,
    test_size=0.50,
    random_state=42,
    stratify=remainder["category"],
)

parts = {"train": train, "validation": validation, "test": test}

# Check that no message appears in separate sets.
keys = {
    name: set(part["instruction"].str.casefold())
    for name, part in parts.items()
}

assert keys["train"].isdisjoint(keys["validation"])
assert keys["train"].isdisjoint(keys["test"])
assert keys["validation"].isdisjoint(keys["test"])

# Check that we kept all rows.
assert sum(len(part) for part in parts.values()) == len(df)

for name, part in parts.items():
    part.to_csv(processed_dir / f"{name}.csv", index=False)
    print(f"\n{name}: {len(part)} rows")
    print(part["category"].value_counts().sort_index())

print("\nChecks passed: no message overlap, all rows accounted for.")