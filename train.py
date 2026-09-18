# Run this file from the submission folder to reproduce the analysis.
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
from sklearn.model_selection import train_test_split, KFold, GridSearchCV, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.neighbors import KNeighborsRegressor
from stable_knn import StableKNNRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.inspection import permutation_importance

SEED = 42
ROOT = Path.cwd()
if not (ROOT / "data/housing_sales.csv").exists():
    ROOT = ROOT / "submission"
for folder in ["results", "figures", "model"]:
    (ROOT / folder).mkdir(exist_ok=True)
pd.set_option("display.max_columns", 20)
plt.rcParams.update({"figure.dpi": 120, "font.size": 10})

data = pd.read_csv(ROOT / "data/housing_sales.csv")
data["sale_date"] = pd.to_datetime(data["sale_date"])
assert len(data) >= 100
assert data.groupby("suburb").size().min() >= 30
assert not data.duplicated(["address", "suburb", "sale_date"]).any()
assert data["property_id"].is_unique
assert data["sale_price_aud"].notna().all()
assert (data["sale_price_aud"] > 0).all()
assert (data["sale_date"] <= pd.Timestamp("2026-09-16")).all()
display(data.groupby("suburb").size().rename("Properties").to_frame())
display(data.isna().sum().rename("Missing values").to_frame())
display(data.head(5))

comparison_mask = data["comparison_id"].notna()
other = data.loc[~comparison_mask]
train_ids, extra_test_ids = train_test_split(other.index, test_size=14, random_state=SEED,
                                           stratify=other["suburb"])
test_ids = list(data.index[comparison_mask]) + list(extra_test_ids)
train = data.loc[train_ids].copy()
test = data.loc[test_ids].copy()
assert set(train.index).isdisjoint(test.index)
assert len(train) + len(test) == len(data)
split = data[["property_id", "comparison_id"]].copy()
split["split"] = np.where(data.index.isin(train.index), "development", "test")
split.to_csv(ROOT / "data/split.csv", index=False)
print("Development:", len(train), "Test:", len(test))
display(pd.crosstab(data["suburb"], split["split"]))

summary = train.groupby("suburb")["sale_price_aud"].agg(["count", "min", "median", "mean", "max"])
summary.to_csv(ROOT / "results/suburb_summary.csv")
display(summary.round(0))
display(pd.crosstab(train["suburb"], train["property_type"]))
fig, axes = plt.subplots(1, 2, figsize=(10, 3.7))
axes[0].hist(train["sale_price_aud"] / 1e6, bins=16, color="steelblue", edgecolor="white")
axes[0].set(xlabel="Sale price (AUD millions)", ylabel="Properties", title="Development price distribution")
suburbs = ["Parramatta", "Blacktown", "Mosman"]
axes[1].boxplot([train.loc[train.suburb == s, "sale_price_aud"] / 1e6 for s in suburbs], tick_labels=suburbs)
axes[1].set(ylabel="Sale price (AUD millions)", title="Markets have different price ranges")
fig.tight_layout(); fig.savefig(ROOT / "figures/price_distribution.png"); plt.show()

fig, axes = plt.subplots(1, 2, figsize=(10, 3.7))
for suburb in suburbs:
    part = train[train.suburb == suburb]
    axes[0].scatter(part.sale_date, part.sale_price_aud / 1e6, label=suburb, alpha=0.7)
    axes[1].scatter(part.bedrooms, part.sale_price_aud / 1e6, label=suburb, alpha=0.7)
axes[0].set(xlabel="Sale date", ylabel="Price (AUD millions)", title="Dates and prices in the sample")
axes[0].tick_params(axis="x", rotation=35)
axes[1].set(xlabel="Bedrooms", ylabel="Price (AUD millions)", title="Bedrooms alone do not explain price")
axes[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(ROOT / "figures/time_and_bedrooms.png"); plt.show()
monthly = train.assign(month=train.sale_date.dt.to_period("M").astype(str)).groupby(["suburb", "month"])["sale_price_aud"].agg(["count", "median"])
monthly.to_csv(ROOT / "results/monthly_summary.csv")
display(monthly)
print("Monthly medians mix property types and often use very few sales. They do not establish market growth.")
q1, q3 = train.sale_price_aud.quantile([0.25, 0.75])
outliers = train[train.sale_price_aud > q3 + 1.5 * (q3-q1)]
display(outliers[["property_id", "suburb", "property_type", "sale_price_aud"]])

def make_features(frame):
    features = frame[["suburb", "property_type", "bedrooms", "bathrooms", "parking"]].copy()
    dates = pd.to_datetime(frame["sale_date"])
    features["sale_month"] = (dates.dt.year - 2025) * 12 + dates.dt.month - 1
    features["bathrooms_per_bedroom"] = features["bathrooms"] / features["bedrooms"].clip(lower=1)
    return features

X_train, X_test = make_features(train), make_features(test)
y_train, y_test = train["sale_price_aud"], test["sale_price_aud"]
numeric = ["bedrooms", "bathrooms", "parking", "sale_month", "bathrooms_per_bedroom"]
categorical = ["suburb", "property_type"]
def make_pipeline(model):
    number_steps = Pipeline([("imputer", SimpleImputer(strategy="median")),
                             ("scaler", StandardScaler())])
    preprocessing = ColumnTransformer([
        ("numbers", number_steps, numeric),
        ("categories", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical)
    ])
    return Pipeline([("preprocess", preprocessing), ("model", model)])
display(X_train.head())

folds = KFold(n_splits=5, shuffle=True, random_state=SEED)
scoring = {"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error", "r2": "r2"}
candidates = {
    "KNN": (StableKNNRegressor(), {"model__n_neighbors": [3, 5, 9]}),
    "Decision tree": (DecisionTreeRegressor(random_state=SEED, min_samples_leaf=3),
                      {"model__max_depth": [2, 4, None]}),
    "Random forest": (RandomForestRegressor(n_estimators=200, min_samples_leaf=2,
                                            max_features=0.8, random_state=SEED),
                      {"model__max_depth": [4, None]})
}
searches, cv_rows, setting_rows = {}, [], []
for name, (estimator, settings) in candidates.items():
    search = GridSearchCV(make_pipeline(estimator), settings, scoring=scoring, refit="mae",
                          cv=folds, return_train_score=True, n_jobs=1)
    search.fit(X_train, y_train)
    searches[name] = search
    results = search.cv_results_
    best = search.best_index_
    cv_rows.append({"model": name, "train_mae": -results["mean_train_mae"][best],
                    "cv_mae": -results["mean_test_mae"][best], "cv_mae_sd": results["std_test_mae"][best],
                    "cv_rmse": -results["mean_test_rmse"][best], "cv_r2": results["mean_test_r2"][best],
                    "settings": str(search.best_params_)})
    for i, params in enumerate(results["params"]):
        setting_rows.append({"model": name, "settings": str(params),
                             "train_mae": -results["mean_train_mae"][i],
                             "cv_mae": -results["mean_test_mae"][i]})
cv_results = pd.DataFrame(cv_rows).sort_values("cv_mae")
cv_results.to_csv(ROOT / "results/cross_validation.csv", index=False)
settings_results = pd.DataFrame(setting_rows)
settings_results.to_csv(ROOT / "results/model_complexity.csv", index=False)
display(cv_results.round(3)); display(settings_results.round(0))
baseline = make_pipeline(DummyRegressor(strategy="median"))
base_cv = cross_validate(baseline, X_train, y_train, cv=folds, scoring=scoring)
print("Median-baseline CV MAE:", round(-base_cv["test_mae"].mean()))
best_name = cv_results.iloc[0]["model"]
best_model = searches[best_name].best_estimator_
print("Selected using CV only:", best_name)

fig, axes = plt.subplots(1, 3, figsize=(11, 3.3))
for ax, name in zip(axes, candidates):
    part = settings_results[settings_results.model == name]
    labels = [s.replace("model__", "") for s in part.settings]
    ax.plot(range(len(part)), part.train_mae / 1000, "o-", label="Training")
    ax.plot(range(len(part)), part.cv_mae / 1000, "o-", label="Validation")
    ax.set_xticks(range(len(part)), labels, rotation=25, ha="right", fontsize=7)
    ax.set(title=name, ylabel="MAE (AUD thousands)")
axes[0].legend(fontsize=8)
fig.tight_layout(); fig.savefig(ROOT / "figures/complexity.png"); plt.show()
winner = cv_results.iloc[0]
display(Markdown(f"**CV finding:** {best_name} has the lowest mean MAE (${winner.cv_mae:,.0f}). "
                 f"Its training MAE is ${winner.train_mae:,.0f}, so its training-validation gap is "
                 f"${winner.cv_mae-winner.train_mae:,.0f}. The CV standard deviation is ${winner.cv_mae_sd:,.0f}; "
                 "five folds are too few to claim a certain ranking. Check both the gap and absolute errors: "
                 "low training error with larger validation error suggests overfitting; large errors in both suggest underfitting."))
print("The initial random-forest expectation was", "supported." if best_name == "Random forest" else "not supported.")

def metric_row(actual, predicted):
    return {"mae": mean_absolute_error(actual, predicted),
            "rmse": np.sqrt(mean_squared_error(actual, predicted)),
            "r2": r2_score(actual, predicted)}

test_rows = []
for name, search in searches.items():
    test_rows.append({"model": name, **metric_row(y_test, search.predict(X_test))})
baseline.fit(X_train, y_train)
test_rows.append({"model": "Median baseline", **metric_row(y_test, baseline.predict(X_test))})
test_metrics = pd.DataFrame(test_rows)
test_metrics.to_csv(ROOT / "results/test_metrics.csv", index=False)
display(test_metrics.round(3))
predictions = best_model.predict(X_test)
test_output = test.copy()
test_output["predicted_price_aud"] = predictions
test_output["signed_error_aud"] = predictions - y_test

test_output["absolute_error_aud"] = abs(test_output["signed_error_aud"])
test_output["absolute_percentage_error"] = 100 * test_output.absolute_error_aud / test_output.sale_price_aud
test_output.to_csv(ROOT / "results/test_predictions.csv", index=False)
subgroup_rows = []
for suburb, group in test_output.groupby("suburb"):
    subgroup_rows.append({"suburb": suburb, "n": len(group),
                          **metric_row(group.sale_price_aud, group.predicted_price_aud),
                          "mape_percent": group.absolute_percentage_error.mean()})
subgroup_metrics = pd.DataFrame(subgroup_rows)
subgroup_metrics.to_csv(ROOT / "results/subgroup_metrics.csv", index=False)
display(subgroup_metrics.round(2))
fig, axes = plt.subplots(1, 2, figsize=(10, 3.7))
axes[0].scatter(y_test / 1e6, predictions / 1e6)
limit = max(y_test.max(), predictions.max()) / 1e6
axes[0].plot([0, limit], [0, limit], "--", color="grey")
axes[0].set(xlabel="Actual (AUD millions)", ylabel="Predicted (AUD millions)", title="Held-out predictions")
axes[1].scatter(predictions / 1e6, (predictions-y_test) / 1e6)
axes[1].axhline(0, linestyle="--", color="grey")
axes[1].set(xlabel="Predicted (AUD millions)", ylabel="Prediction minus actual (millions)", title="Held-out residuals")
fig.tight_layout(); fig.savefig(ROOT / "figures/test_errors.png"); plt.show()

from sklearn.base import clone
importance_rows = []
for fold_number, (fit_rows, valid_rows) in enumerate(folds.split(X_train), start=1):
    fold_model = clone(best_model).fit(X_train.iloc[fit_rows], y_train.iloc[fit_rows])
    importance = permutation_importance(fold_model, X_train.iloc[valid_rows], y_train.iloc[valid_rows],
                                         scoring="neg_mean_absolute_error", n_repeats=10, random_state=SEED)
    importance_rows.append(importance.importances_mean)
importance_table = pd.DataFrame({"feature": X_train.columns,
                                 "mae_increase": np.mean(importance_rows, axis=0),
                                 "fold_sd": np.std(importance_rows, axis=0)}).sort_values("mae_increase", ascending=False)
importance_table.to_csv(ROOT / "results/feature_importance.csv", index=False)
display(importance_table.round(0))
fig, ax = plt.subplots(figsize=(7, 3.4))
part = importance_table.sort_values("mae_increase")
ax.barh(part.feature, part.mae_increase / 1000, color="steelblue")
ax.set(xlabel="Validation MAE increase (AUD thousands)", title="Exploratory permutation importance")
fig.tight_layout(); fig.savefig(ROOT / "figures/importance.png"); plt.show()

failures = test_output.nlargest(5, "absolute_error_aud")
failures.to_csv(ROOT / "results/five_largest_errors.csv", index=False)
display(failures[["property_id", "address", "suburb", "property_type", "bedrooms", "bathrooms", "parking",
                  "sale_price_aud", "predicted_price_aud", "signed_error_aud", "absolute_percentage_error"]].round(1))
print("Training target range:", f"${y_train.min():,.0f} to ${y_train.max():,.0f}")
print("Test errors are retained, including unusual high-price properties. They are not removed to improve scores.")

if best_name == "KNN":
    fitted_knn = best_model.named_steps["model"]
    failure_features = best_model.named_steps["preprocess"].transform(make_features(failures))
    squared = np.sum((failure_features[:, None, :] - fitted_knn._fit_X[None, :, :]) ** 2, axis=2)
    positions = np.argsort(np.round(squared, 12), axis=1, kind="stable")[:, :fitted_knn.n_neighbors]
    distances = np.sqrt(np.take_along_axis(squared, positions, axis=1))
    neighbour_rows = []
    for case, distance_row, position_row in zip(failures.itertuples(), distances, positions):
        for distance, position in zip(distance_row, position_row):
            neighbour = train.iloc[position]
            neighbour_rows.append({"test_property": case.property_id, "neighbour_id": neighbour.property_id,
                                   "suburb": neighbour.suburb, "price": neighbour.sale_price_aud,
                                   "distance": distance})
    neighbour_table = pd.DataFrame(neighbour_rows)
    neighbour_table.to_csv(ROOT / "results/failure_neighbours.csv", index=False)
    display(neighbour_table.round(3))

human = pd.read_csv(ROOT / "data/comparison_blind.csv")
llm = pd.read_csv(ROOT / "data/llm_estimates.csv")
assert human.comparison_id.is_unique and llm.comparison_id.is_unique
assert set(human.comparison_id) == set(llm.comparison_id)
comparison = test_output[test_output.comparison_id.notna()].merge(llm, on="comparison_id", validate="one_to_one")
comparison = comparison.merge(human[["comparison_id", "human_estimate_aud"]], on="comparison_id", validate="one_to_one")
comparison = comparison.sort_values("comparison_id")
comparison.to_csv(ROOT / "results/ten_property_comparison.csv", index=False)
display(comparison[["comparison_id", "suburb", "sale_price_aud", "predicted_price_aud",
                    "llm_estimate_aud", "human_estimate_aud"]].round(0))
comparison_scores = []
for label, column in [("ML", "predicted_price_aud"), ("LLM", "llm_estimate_aud"), ("Student (non-blind)", "human_estimate_aud")]:
    values = pd.to_numeric(comparison[column], errors="coerce")
    if values.notna().all() and np.isfinite(values).all() and (values > 0).all():
        comparison_scores.append({"approach": label, **metric_row(comparison.sale_price_aud, values)})
    else:
        print(label + " comparison incomplete: ten positive estimates are required.")
comparison_metrics = pd.DataFrame(comparison_scores)
comparison_metrics.to_csv(ROOT / "results/comparison_metrics.csv", index=False)
display(comparison_metrics.round(3))
print("Student estimates were supplied after price/example disclosure; scores do not establish independent human superiority.")

illustrative = pd.read_csv(ROOT / "data/illustrative_estimates.csv")
comparison = comparison.merge(illustrative, on="comparison_id", validate="one_to_one")
comparison.to_csv(ROOT / "results/ten_property_comparison.csv", index=False)
display(comparison[["comparison_id", "sale_price_aud", "predicted_price_aud", "llm_estimate_aud", "illustrative_estimate_aud"]].round(0))
print("Illustrative-only errors (not human evidence):", metric_row(comparison.sale_price_aud, comparison.illustrative_estimate_aud))

joblib.dump(best_model, ROOT / "model/housing_model.joblib")
metadata = {"selected_model": best_name, "development_n": len(train), "test_n": len(test),
            "total_n": len(data), "seed": SEED, "numeric": numeric, "categorical": categorical,
            "test_metrics": metric_row(y_test, predictions),
            "training_min_date": str(train.sale_date.min().date()),
            "training_max_date": str(train.sale_date.max().date()),
            "training_min_price": int(y_train.min()), "training_max_price": int(y_train.max()),
            "human_complete": bool(human.human_estimate_aud.notna().all()),
            "human_blinded": False}
(ROOT / "results/summary.json").write_text(json.dumps(metadata, indent=2))
print("Saved fitted model and results.")
print("Selected model:", best_name)
print("Run the local application with: python app.py")
