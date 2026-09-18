# Decisions recorded before modelling

Suburbs confirmed by the student: Parramatta, Blacktown and Mosman.
Target: publicly disclosed sold price in Australian dollars.

Expected strongest variables, before feature engineering: suburb (different markets), property type (house versus unit), and bedrooms (a rough measure of accommodation). Advertised area could help, but listing cards often mix land and floor area, so retain it for the audit and exclude it from the initial model.

Models: KNN regression (similar examples), a decision tree (simple splitting rules), and random forest regression (averaging different trees). Expect random forest to perform best because averaging reduces the instability of a single tree. This is a hypothesis, not a result.

Hold out 10 specifically blinded comparison properties before viewing their prices, plus a seeded, suburb-stratified sample of other records. Five-fold cross-validation on the remaining development set will select the model using MAE. Try small predeclared settings: KNN k=3,5,9; tree depth=2,4,unlimited with at least 3 samples per leaf; forest 200 trees, depth=4 or unlimited, min_samples_leaf=2, max_features=0.8. Use the same folds and fit all imputation, encoding and scaling inside each fold. Report MAE, RMSE and R-squared, with a training-median baseline.

Engineer only a sale-month index and bathroom/bedroom ratio, neither using price. Explore prices using the development set first. Exclude address, source URL, sale method and area from model inputs. Do not infer a missing parking count as zero.

The LLM comparison will be an estimate recorded in this Codex conversation with each selected target hidden. Earlier training-market examples have already been seen, so this is not a fresh-context LLM experiment. Human estimates must come from the student and must be recorded before revealing the selected actual prices or ML/LLM predictions.
