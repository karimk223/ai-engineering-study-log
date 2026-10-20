from pathlib import Path

import pandas as pd


base_dir = Path(__file__).resolve().parent

df = pd.read_csv(
    base_dir / "data" / "raw" / "customer_support.csv",
    usecols=["instruction", "category"],
    dtype="string",
)

# Clean all original categories directly from the verified raw source.
starting_rows = len(df)
full = df.dropna(subset=["instruction", "category"]).copy()
full["instruction"] = (
    full["instruction"]
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)
full["category"] = full["category"].str.strip()
full = full.loc[
    full["instruction"].ne("") & full["category"].ne("")
].copy()

print("Missing/blank rows removed:", starting_rows - len(full))

full["_text_key"] = full["instruction"].str.casefold()
label_counts = full.groupby("_text_key")["category"].nunique()

if (label_counts > 1).any():
    raise ValueError("Conflicting labels found. Review before continuing.")

cleaned = full.drop_duplicates(subset="_text_key").drop(columns="_text_key")
print("Duplicates removed:", len(full) - len(cleaned))

output_dir = base_dir / "data" / "processed" / "full"
output_dir.mkdir(parents=True, exist_ok=True)
cleaned.to_csv(output_dir / "support_tickets.csv", index=False)

print("Rows:", len(cleaned))
print("Categories:", cleaned["category"].nunique())
print(cleaned["category"].value_counts().sort_index())
