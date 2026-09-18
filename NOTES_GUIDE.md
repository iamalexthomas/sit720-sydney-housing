# Beginner guide to the supplied notes

All 13 Week 8 screenshots and all 11 Week 9 screenshots were reviewed. Their embedded videos were not accessible from screenshots. The project uses the ideas below in regression form.

## Week 8

- 8.1 introduces KNN and decision trees.
- 8.2-8.3: KNN finds nearby training examples using a distance such as Euclidean distance. Classification uses the most common label; regression averages numeric targets. Distance weighting gives closer neighbours greater influence. Features must have sensible scales; numeric codes must not imply that one suburb is twice another.
- 8.4: small k follows local detail but can be noisy (high variance). Larger k smooths predictions but can miss useful detail (high bias). Choose k on validation data.
- 8.5-8.6: a regression tree repeatedly splits data using one feature and threshold. It chooses splits that reduce squared error. A leaf predicts its training targets' mean. This is a greedy procedure rather than a search through every possible tree.
- 8.7-8.8: classification trees use class-purity measures such as Gini or entropy. ID3 and C4.5 are classification algorithms. CART also supports regression, where squared-error reduction replaces classification impurity. Accuracy and Gini are not appropriate price-prediction scores.
- 8.9: deep trees can memorise training data. Pre-pruning stops growth (for example maximum depth or minimum leaf size). Post-pruning removes branches after growth.
- 8.10: trees are understandable and capture nonlinear patterns, but small data changes can alter the splits. Tree splits are axis-aligned.
- 8.11: distance choice matters for KNN; feature importance helps explain tree models, but importance is not causation.
- 8.12-8.13: the practicals use scikit-learn, a fixed train/test split, fitting, predictions and comparisons across model complexity. This project follows that structure, with regression estimators and leakage-safe preprocessing.

## Week 9

- 9.1-9.2: an ensemble combines several models. Averaging less-correlated models can reduce variance.
- 9.3: bootstrap sampling draws with replacement. It commonly draws the same number of rows as the original training set, but some rows appear repeatedly and others are absent; it need not be a smaller draw.
- 9.4: AdaBoost fits weak learners sequentially, increasing attention to difficult observations. It differs from bagging, whose models can be fitted independently.
- 9.5: bagging fits models on bootstrap samples and averages numeric predictions (or votes for classes).
- 9.6: random forest adds random feature subsets at splits to make trees less similar. The number of trees controls ensemble stability and computing cost. Increasing the number of trees generally stabilises predictions; it does not automatically cause the same overfitting as increasing one tree's depth.
- 9.7: out-of-bag predictions use only trees whose bootstrap sample omitted that training row. About 36.8% of original rows are omitted by one large bootstrap sample of equal size. Preprocessing fitted on all rows can still contaminate this estimate. We use fold-contained preprocessing and k-fold CV instead.
- 9.8: voting combines predictions directly; stacking learns a second model from out-of-fold predictions. Both need careful validation. They are beyond the required three-model comparison here.
- 9.9-9.11: the practicals fit forest/AdaBoost classifiers and inspect importance and errors. For housing use RandomForestRegressor and MAE/RMSE, not classification accuracy or confusion matrices.

## How to explain this project in a viva

1. What is the target? A sold price in Australian dollars.
2. Why scale? Otherwise large-valued features dominate KNN distances.
3. Why hold out test cases? To measure performance on examples not used to choose the model.
4. What is leakage? Information from validation/test examples influencing training or model choices.
5. Why did the most expensive house fail? Its rare luxury context was missing and its price exceeded every training target.
6. Why did one Blacktown house get overvalued? Its nearest neighbours included expensive Mosman properties because room counts and other numeric features affected distance strongly.
7. Why not claim human judgement lost? No real human estimates were supplied. The illustrative values were AI-generated after outcomes were available.
8. What would you improve first? Collect more consistent, representative data and better location/condition features; then evaluate on later dates and separate buildings.
