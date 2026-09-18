"""Export the fitted KNN pipeline for the small JavaScript application."""
from pathlib import Path
import json
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent
model = joblib.load(ROOT / 'model/housing_model.joblib')
preprocess = model.named_steps['preprocess']
numbers = preprocess.named_transformers_['numbers']
knn = model.named_steps['model']
if type(knn).__name__ not in ['KNeighborsRegressor', 'StableKNNRegressor']:
    raise ValueError('This browser export supports the selected KNN model only. Update it if the selected model changes.')
metadata = json.loads((ROOT / 'results/summary.json').read_text())
export = {
    'model_name': 'KNN regression', 'k': int(knn.n_neighbors),
    'medians': numbers.named_steps['imputer'].statistics_.tolist(),
    'means': numbers.named_steps['scaler'].mean_.tolist(),
    'scales': numbers.named_steps['scaler'].scale_.tolist(),
    'categories': [v.tolist() for v in preprocess.named_transformers_['categories'].categories_],
    'training_features': knn._fit_X.tolist(), 'training_targets': knn._y.tolist(),
    'metadata': metadata
}
path = ROOT / 'site/dist/model.json'
path.write_text(json.dumps(export))
print('Exported', len(export['training_targets']), 'training examples to', path.name)
