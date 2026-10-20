from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline


processed_dir = (
    Path(__file__).resolve().parent / "data" / "processed" / "full"
)

train = pd.read_csv(processed_dir / "train.csv", dtype="string")
validation = pd.read_csv(
    processed_dir / "validation.csv", dtype="string"
)

X_train = train["instruction"]
y_train = train["category"]

X_validation = validation["instruction"]
y_validation = validation["category"]

# Simple comparison: always predict the most common training category.
baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(train[["instruction"]], y_train)

# Learn text features and classification from training data only.
model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
    ("classifier", LogisticRegression(max_iter=1000)),
])
model.fit(X_train, y_train)

# Predict validation answers without learning from them.
model_predictions = model.predict(X_validation)

results = {
    "Baseline": baseline.predict(validation[["instruction"]]),
    "TF-IDF + logistic regression": model_predictions,
}

for name, predictions in results.items():
    print(f"\n{name}")
    print(classification_report(
        y_validation,
        predictions,
        labels=model.classes_,
        digits=3,
        zero_division=0,
    ))

mistakes = (y_validation != model_predictions).sum()
print(f"\nModel validation mistakes: {mistakes}/{len(validation)}")

comparison = validation.assign(predicted=model_predictions)

error_rows = comparison.loc[
    comparison["category"] != comparison["predicted"],
    ["instruction", "category", "predicted"],
]

print("\nValidation disagreements:")
print(error_rows.to_string(index=False))

# Evaluate on the reserved test data without learning from it.
test = pd.read_csv(processed_dir / "test.csv", dtype="string")
test_predictions = model.predict(test["instruction"])

for name, predictions in {
    "Final test — baseline": baseline.predict(test[["instruction"]]),
    "Final test — model": test_predictions,
}.items():
    print(f"\n{name}")
    print(classification_report(
        test["category"],
        predictions,
        labels=model.classes_,
        digits=3,
        zero_division=0,
    ))

# Save the text converter and classifier together.
artifact_dir = Path(__file__).resolve().parent / "artifacts"
artifact_dir.mkdir(parents=True, exist_ok=True)
artifact_path = artifact_dir / "ticket_router_full_v1.joblib"

bundle = {
    "model_version": "ticket-router-full-v1",
    "pipeline": model,
    "categories": model.classes_.tolist(),
    "sklearn_version": sklearn.__version__,
}

joblib.dump(bundle, artifact_path)

# Check that loading our own saved model preserves its predictions.
loaded = joblib.load(artifact_path)
restored_predictions = loaded["pipeline"].predict(test["instruction"])

assert (restored_predictions == test_predictions).all()

print(f"\nSaved: {artifact_path}")
print("Reload check passed: predictions unchanged.")
