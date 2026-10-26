# Compact ML revision notebook

[ml_revision.ipynb](ml_revision.ipynb) uses one small flower table to practise three different tasks:

- **Prediction:** learn species names from labeled examples, then check guesses on other flowers.
- **Grouping:** put flowers with similar measurements together without supplying species names.
- **Visualization:** combine four measurements into two scores so each flower can be drawn as a dot.

The notebook uses scikit-learn's bundled Iris dataset: 150 flowers, four numeric measurements and three known species. `load_iris()` loads the included dataset locally. No separate dataset download, provider account or model weights are needed.

## Setup and run

The observed learner run used Python 3.12.13 in the existing `projects/fastapi_02_ml_prediction_api/.venv` environment, with notebook and plotting packages added during setup. The four direct package versions used by this notebook are recorded in [requirements.txt](requirements.txt). They are direct pins, not a lock of every transitive dependency.

For a separate notebook environment, run these commands from the repository root:

```bash
python3.12 -m venv notebooks/.venv
notebooks/.venv/bin/python -m pip install -r notebooks/requirements.txt
```

In VS Code:

1. Enable the Python and Jupyter extensions and open `notebooks/ml_revision.ipynb`.
2. Select the notebook environment's Python as its kernel. For the setup above, use `notebooks/.venv/bin/python`; the existing learner environment also works.
3. Restart the kernel, run all cells from the top, and save the notebook with its outputs and chart. Dependencies are installed during setup rather than inside the exercise cells.

The learner completed the cleanup and reported restarting the kernel and running all cells. The saved notebook confirms seven code cells executed in order from 1 to 7, no saved errors, matching numeric results, an embedded chart and a final explanatory Markdown cell. The separate environment installation above has not been performed or verified. The current environment passes `pip check`.

## Observed results

| Exercise | Learner-run result |
| --- | --- |
| Inspect data | 150 rows, four measurement columns, zero missing measurements |
| Training/test split | 120 training flowers, 30 test flowers; stratified, seed 42 |
| Always guess one species | 10/30 correct, 33.3% |
| Decision tree, depth at most three | 29/30 correct, 96.7% |
| K-Means, three requested groups | Group 0: 53; group 1: 50; group 2: 47 |
| PCA, four coordinates to two | Ratios 0.72962445 and 0.22850762; total variance retained 95.8% |
| Chart | Two PCA coordinates per dot, colored by its existing K-Means group |

The tree learns only from the training flowers. Its test result is a small demonstration on one split. Scaling, K-Means and PCA use all 150 flowers in a separate descriptive exercise; they are not part of this classifier's test pipeline.

## Understand the chart

Each dot is one flower. PCA supplies its horizontal and vertical coordinates, and K-Means supplies its group color. The decision tree is a separate prediction experiment and does not supply the chart's colors. Group IDs are arbitrary and have not been evaluated against the true species.

PCA makes two summary numbers from four measurements, losing some detail. Its 95.8% retained-variance figure concerns that numerical representation, while the tree's 96.7% figure concerns correct species guesses. The learning notes explain the difference with examples.

See [NOTES.md](NOTES.md) for plain-language definitions, the whole exercise's story, PCA examples and the exact evidence behind these observations. The notebook's embedded chart can be kept in Git; environments, notebook checkpoints and package caches should remain excluded.
