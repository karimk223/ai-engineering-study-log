# Iris ML — technical notes

Definitions, examples and interpretation for the Iris classification, clustering and PCA notebook.

## The whole exercise, in everyday words

We started with a table of 150 flowers. Each flower has four measurements: length and width of its petals and sepals (the outer leaf-like parts around the petals). We also have the real species name for each flower. A measurement is an input, called a feature; the species name is the answer, called a label.

We used that same table for three different questions:

1. **Can a computer learn to name a flower from its measurements?** We showed a decision tree 120 flowers together with their known species. It learned questions about measurements, then guessed the species of 30 other flowers whose answers were kept out of training. It got 29 right. A simple baseline that always guessed the same species got 10 right. This taught us learning from examples with answers, called supervised classification.
2. **Which flowers have similar measurements if we hide the species names?** After making column scales comparable, we asked K-Means to make three groups. It grouped flowers using their four measurements, producing sizes 53, 50 and 47. The group names 0, 1 and 2 were assigned by the program. We have not checked which true species each group contains. This taught us clustering without supplied answers.
3. **How can we draw flowers that each have four measurements on a flat graph with only two axes?** PCA calculated two combined scores per flower from the four standardized measurements. One score supplies the horizontal position and one the vertical position. They preserve 95.8% of the total measurement variance; all 150 flowers remain. This taught us reducing the number of coordinates for a useful picture.

The final chart combines the last two answers: PCA determines each dot's position, and the existing K-Means group determines its color. The decision tree is a separate experiment and supplies neither positions nor colors. K-Means was fitted on four standardized measurements, before the two-coordinate projection was plotted. A purple dot means group 0, a teal dot group 1, and a yellow dot group 2; the colors are not species names.

**What the picture shows:** the teal group is clearly separated toward the left, while the purple and yellow groups are closer and partly overlap on the right in this projection. Proximity on this two-dimensional view suggests similar PCA coordinates; it does not preserve every original distance exactly or establish agreement with species. The chart visualizes the groups rather than scoring prediction accuracy.

**PCA without formulas:** imagine four exam scores: Maths80, Physics82, History60 and Geography62. Two simple summaries could be science81 and humanities61. Four numbers became two, with some detail lost: science81 alone does not reveal that the original scores were80and82. This is an analogy for summarizing related measurements. Actual PCA automatically learns two mixing recipes from the full flower table; it does not manually choose subject pairs or necessarily average them equally. Each flower's two summary numbers give its horizontal and vertical position on our chart. Start with this explanation before the optional mathematical details below.

## Basic words

- **Features:** the input measurements a model receives. In the Iris exercise, one flower has four measurements (sepal length/width and petal length/width).
- **Target or label:** the known answer we would ask a supervised model to predict. Iris includes flower species labels, but the first PCA exercise will not use them.
- **Supervised learning:** learn from examples that include both features and correct answers. Our existing ticket classifier learned from customer messages paired with categories.
- **Unsupervised learning:** look for structure in inputs without supplying the correct answer for each example. PCA is one such method.
- **Classification versus regression:** classification predicts a category, such as REFUND; regression predicts a number, such as a price. Both can be supervised tasks.

## Baseline, decision tree and accuracy

A **baseline** is a simple reference to compare a model against. Our `DummyClassifier(strategy="most_frequent")` always predicts the most common training species and ignores the input measurements. The training classes are tied in this split; it selects one tied class consistently.

A **decision tree** learns measurement-based questions, such as whether a petal length is below a learned threshold, then follows the answers down its branches to a predicted species. `fit` learns from training examples; `predict` applies the learned rules to new feature rows.

`max_depth=3` allows at most three successive splits along any root-to-leaf path. Some paths may finish earlier. This limits the tree's complexity and can reduce **overfitting**: learning details of the training examples that do not help with new flowers. A shallow tree can also miss useful patterns, so depth three is a simple starting choice, not a proven best setting.

`random_state=42` supplies a fixed seed for repeatable random choices with the same data and software. In a decision tree this includes choices between equally good splits; in `train_test_split` it controls the shuffled split. The number 42 is arbitrary and does not increase accuracy by itself.

**Accuracy** is correct predictions divided by the total evaluated examples. Our held-out result was baseline `10/30` (33.3%) and decision tree `29/30` (96.7%), so the tree made one error on this particular test split. This is a small educational comparison, not evidence that every future dataset will have the same accuracy. The tree was fitted only on the 120 training flowers and used no feature scaling.

## K-Means grouping

**Clustering** groups examples by similarity. **K-Means** alternates between assigning flowers to a nearby group center and moving each center to the average of its assigned flowers. We chose three groups for this demonstration and supplied only the four measurements. It did not receive the correct species labels. Group IDs such as 0, 1 and 2 are arbitrary names and do not automatically match species IDs.

We standardized each column before grouping so its numerical spread would not dominate the distance calculation. This descriptive exercise used all 150 flowers and reported group sizes; it did not estimate performance on unseen flowers. `n_init=10` tries ten starting arrangements and keeps the one with the lowest within-group squared-distance sum. The resulting groups contain 53, 50 and 47 flowers, totaling 150. These counts describe the grouping, not its agreement with species. Three groups were requested explicitly; this run did not discover the best number of groups.

## PCA in simple terms

**Principal component analysis (PCA)** makes new measurements by combining the old ones. It chooses directions where the data varies most. Keeping two components gives each flower two new numbers instead of its original four, making a simple plot possible. The two new numbers are not sepal or petal measurements and are not the flower species.

**Variance** means how spread out values are. `explained_variance_ratio_` reports how much of the standardized input's measured spread each retained component captures. Adding its two values gives the share captured by both components together. This is about variation in the measurements, not classification accuracy or proof that the two numbers keep everything useful for predicting species.

**Variation retained, using our actual output:** the four standardized measurements have a total amount of spread across the 150 flowers. PCA's first direction captures 72.962445% of that total and its second captures 22.850762%. Together they retain 95.813207% (displayed as 95.8%); the two discarded directions account for about 4.2%. All 150 flowers remain, each with two combined coordinates instead of four original measurements. Related measurements can share patterns: for example, if longer petals also tend to be wider, some variation can be described by one combined direction. Retained variance measures preserved spread, not the percentage of correct species predictions or the percentage of flowers kept.

**A concrete compression example:** the first flower's four real measurements are `[5.1, 3.5, 1.4, 0.2]` cm. Its two PCA scores are approximately `[-2.265, 0.480]`. Using those scores plus the fitted PCA and scaler transformations to reconstruct the four measurements gives approximately `[5.019, 3.515, 1.466, 0.252]` cm. The reconstructed numbers are close but not identical: reducing four coordinates to two lost some detail. The fitted transformation is needed to decode the scores; two numbers alone do not independently encode the full dataset. This illustrates the inverse transformation; the notebook itself stops at the two-coordinate plot.

**What 95.8% means through reconstruction:** compare two ways of approximating the whole table. One gives every flower the column averages; the other rebuilds each flower from its own two PCA scores. Summing squared errors on standardized measurements gives `600.0` for the averages and approximately `25.120757` for the two-score reconstruction. The second error is `4.186793%` of the first, so the retained-variance score is `100% - 4.186793% = 95.813207%`. Equivalently, if the average-only reconstruction has 100 error points, PCA leaves about 4.2 points. This is a table-wide statistic relative to that reference; it does not mean each measurement is within 4.2% of its real value.

**How the two scores are calculated:** a component is a fixed set of mixing weights learned from all the flower measurements; a score is the result of applying that component's weights to one flower. For this dataset, call the four standardized measurements `z1, z2, z3, z4` in the original column order. Rounded learned recipes are `score1 = 0.521*z1 - 0.269*z2 + 0.580*z3 + 0.565*z4` and `score2 = 0.377*z1 + 0.923*z2 + 0.024*z3 + 0.067*z4`. The same recipes apply to every flower; only its input measurements change. The first flower's standardized values are approximately `[-0.901, 1.019, -1.340, -1.315]`, yielding scores approximately `[-2.265, 0.480]` using unrounded weights. PCA chooses the recipes from relationships across the dataset to minimize squared reconstruction error for the chosen number of linear components. It does not receive species answers.

**How reconstruction works:** use those two scores to mix the two learned component patterns back into an estimated four-value standardized row. For example, `estimated_z1 = 0.521*score1 + 0.377*score2`; the other three estimates use their corresponding weights from both recipes. Add the fitted PCA centering offset (approximately zero after our standardization), then undo the scaler to return to centimeters. Keeping all four PCA components would allow reconstruction of the original four standardized values up to numerical precision. We kept two and effectively set the missing two component scores to zero, so the result is an approximation. Two numbers do not uniquely recover four unrelated numbers; the reconstruction follows the relationships learned from the full table.

**What each component's percentage means:** on the chart, component 1 is about 73.0% and component 2 about 22.9%. In the reconstruction example, call the column-average reference error 100 points: keeping the first score removes 72.96 points, leaving 27.04; adding the second score removes another 22.85 points, leaving 4.19. Thus `72.96% + 22.85% = 95.81%`, displayed as `95.8%`. These contributions share the same dataset-wide denominator. Independently rounded chart labels (73.0 and22.9) need not add exactly to the rounded combined percentage. The first recipe captures the most variation; the second captures the largest remaining independent linear pattern.

**Scaling** puts each input measurement on a comparable scale before PCA. `StandardScaler` learns a mean and spread for each column, then centers and rescales values. This descriptive PCA exercise transformed the full built-in Iris table without a prediction train/test split. If PCA becomes part of a prediction pipeline, fit the scaler and PCA on training data only, then apply those learned transformations to validation/test data; fitting on held-out rows would leak information.

## Notebook contents

`ml_revision.ipynb` contains the following experiments:

1. Load and inspect scikit-learn's bundled Iris data (150 flowers, four measurements); check missing values and describe any real cleaning performed. This is a small extract/transform/load exercise, not a claim that the built-in dataset needed substantial cleaning.
2. Compare a simple supervised species classifier against a simple baseline on held-out rows. Fit preprocessing on training rows only and report actual results, not assumed accuracy.
3. Use K-Means to group flowers without supplying species labels. Cluster numbers are arbitrary group names, not predicted species or accuracy scores.
4. Standardize the four measurements and reduce them to two PCA components; report shapes and explained-variance ratios. This is dimensionality reduction, not a species prediction.

## Data and reproduction

The table contains 150 flowers with four numeric measurements and zero missing measurements. Species names are `setosa`, `versicolor` and `virginica`; `iris.target` encodes their labels numerically. A stratified 80/20 split produces 120 training and 30 test flowers. `stratify=labels` preserves the species mix across those portions, and `random_state=42` fixes the shuffle for a repeatable split.

The notebook contains executed outputs and an embedded chart. [README.md](README.md) documents setup and the result table; [requirements.txt](requirements.txt) records the direct package versions. Scaling, clustering and PCA use all 150 flowers for exploration, separately from the classifier's training/test evaluation.
