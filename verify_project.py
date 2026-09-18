from pathlib import Path
import sys,json,subprocess
ROOT = Path(__file__).resolve().parent
import os
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
import pandas as pd
import numpy as np
from prediction import predict_price
from app import app
rows=pd.read_csv('data/housing_sales.csv')[['suburb','property_type','bedrooms','bathrooms','parking','sale_date']]
rows=rows.astype(object).where(rows.notna(),None).to_dict('records')
script="const fs=require('fs');const {predictProperty}=require('./site/dist/predict.js');const m=JSON.parse(fs.readFileSync('./site/dist/model.json'));const rows=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(rows.map(r=>predictProperty(m,r).prediction_aud)));"
js=json.loads(subprocess.check_output(['node','-e',script],input=json.dumps(rows).encode()))
py=[predict_price(r) for r in rows]
diff=np.abs(np.array(js)-py)
print('Max Python/JavaScript difference:',diff.max())
print('Mismatches:',[(i,py[i],js[i]) for i in np.where(diff>0.01)[0]])
assert diff.max()<0.01
client=app.test_client()
assert client.get('/').status_code==200
assert client.get('/model.json').status_code==200
response=client.post('/api/predict',json=rows[0])
assert response.status_code==200 and abs(response.json['prediction_aud']-py[0])<0.01
for bad in [{},dict(rows[0],bedrooms=-1),dict(rows[0],suburb='Unknown'),dict(rows[0],bathrooms='abc'),dict(rows[0],sale_date='invalid')]:
 assert client.post('/api/predict',json=bad).status_code==400
print('Prediction parity and Flask input checks passed.')

data = pd.read_csv("data/housing_sales.csv")
split = pd.read_csv("data/split.csv")
assert len(data) >= 100 and data.groupby("suburb").size().min() >= 30
assert data.property_id.is_unique and (data.sale_price_aud > 0).all()
assert split.property_id.is_unique and set(split.property_id) == set(data.property_id)
assert split["split"].value_counts().to_dict() == {"development": 95, "test": 24}
assert split.loc[split.comparison_id.notna(), "split"].eq("test").all()
assert not data.duplicated(["address", "suburb", "sale_date"]).any()
import nbformat
nb = nbformat.read("SIT720_8_1D.ipynb", as_version=4)
code_cells = [c for c in nb.cells if c.cell_type == "code"]
assert all(c.execution_count is not None for c in code_cells)
assert not any(o.output_type == "error" for c in code_cells for o in c.outputs)
print("Data, split and executed notebook checks passed.")

# Check that the saved headline scores and failure cases match predictions.
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
predictions = pd.read_csv('results/test_predictions.csv')
summary = json.loads(Path('results/summary.json').read_text())
y = predictions.sale_price_aud
p = predictions.predicted_price_aud
calculated = {'mae': mean_absolute_error(y, p),
              'rmse': np.sqrt(mean_squared_error(y, p)),
              'r2': r2_score(y, p)}
for key, value in calculated.items():
    assert np.isclose(value, summary['test_metrics'][key])
assert set(predictions.property_id) == set(split.loc[split['split'] == 'test', 'property_id'])
ranked = predictions.assign(error=(p-y).abs()).sort_values('error', ascending=False)
failures = pd.read_csv('results/five_largest_errors.csv')
assert list(ranked.head(5).property_id) == list(failures.property_id)
comparison = pd.read_csv('results/ten_property_comparison.csv')
assert len(comparison) == 10 and comparison.comparison_id.is_unique
assert set(comparison.property_id).issubset(set(predictions.property_id))
student = pd.read_csv('data/comparison_blind.csv').set_index('comparison_id').human_estimate_aud
actual_student = comparison.set_index('comparison_id').human_estimate_aud
assert student.notna().all() and (student > 0).all()
assert actual_student.sort_index().equals(student.sort_index())
assert summary['human_complete'] and summary['human_blinded'] is False
scores = pd.read_csv('results/comparison_metrics.csv').set_index('approach')
student_scores = scores.loc['Student (non-blind)']
assert np.isclose(student_scores.mae, mean_absolute_error(comparison.sale_price_aud, comparison.human_estimate_aud))
assert np.isclose(student_scores.rmse, np.sqrt(mean_squared_error(comparison.sale_price_aud, comparison.human_estimate_aud)))
assert np.isclose(student_scores.r2, r2_score(comparison.sale_price_aud, comparison.human_estimate_aud))
print('Saved metrics, five largest errors and held-out comparison checks passed.')
