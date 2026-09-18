# Sydney housing price prediction

SIT720 Task 8.1D compares K-nearest neighbours, a decision tree and random forest using 119 sold-property listings from Parramatta, Blacktown and Mosman. Five-fold cross-validation selects the model using 95 development records; 24 properties are reserved for testing.

[Open the housing predictor](https://iamalexthomas.github.io/sit720-sydney-housing/)

## Project files

| File or folder | Contents |
| --- | --- |
| `SIT720_8_1D.ipynb` | Executed analysis, plots, model evaluation and valuation comparison |
| `output/pdf/SIT720_8_1D_report.pdf` | Final report |
| `data/` | Property records, source URLs, transcription checks, split and comparison estimates |
| `train.py` | Runnable analysis and model training |
| `stable_knn.py` | KNN with consistent handling of equal-distance neighbours |
| `model/housing_model.joblib` | Fitted preprocessing and prediction pipeline |
| `results/`, `figures/` | Saved results, charts and application screenshots |
| `app.py`, `prediction.py` | Flask application and Python prediction endpoint |
| `site/dist/` | Static web application and exported model |
| `export_model.py` | Export the fitted KNN model for browser prediction |
| `verify_project.py` | Data, split, prediction and endpoint checks |

## Setup

Tested with Python 3.14 on Linux. Run these commands from the project folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`. Open the notebook in VS Code or Jupyter, select this environment, then restart the kernel and run all cells. If needed, install JupyterLab with `python -m pip install jupyterlab`.

## Reproduce the results

```bash
python train.py
python export_model.py
python verify_project.py
```

Verification also requires Node.js. The dataset is included, so training and prediction do not require live listing downloads or API keys. The final report is provided in `output/pdf/`.

Preprocessing is fitted within each cross-validation fold. The split uses seed 42 and includes ten preselected comparison properties plus fourteen additional cases sampled by suburb. Model selection uses development cross-validation; the saved model is trained on the 95 development properties.

## Run the application

```bash
python app.py
```

Open `http://127.0.0.1:5000`. Select the suburb and property type, enter room counts, parking and a sale date, then click **Predict price**. Use zero bedrooms for a studio and leave parking blank when unknown.

Example: a Parramatta apartment with two bedrooms, two bathrooms, one parking space and a sale date of 1 August 2026 returns approximately **$692,333**.

To serve the static version:

```bash
python -m http.server 8000 --directory site/dist
```

Open `http://127.0.0.1:8000`. Serve the files over HTTP so the browser can load `model.json`. The GitHub Pages workflow in `.github/workflows/pages.yml` publishes `site/dist` when changes are pushed to `main`.

## Data and interpretation

The dataset contains 37 Parramatta, 43 Blacktown and 39 Mosman properties transcribed from Domain and realestate.com.au listings. Source URLs and access dates are retained in the CSV. Advertised area is excluded from modelling because its definitions are inconsistent; missing parking is imputed within the fitted pipeline.

The notebook compares model, LLM and personal estimates for ten held-out properties. Personal estimates were recorded after prices and example estimates were available, so their errors describe agreement with the outcomes rather than independent forecasting performance. Recording conditions and the LLM prompt are included in the notebook.

The selected KNN model has a test MAE of approximately $1.20 million. Rare luxury properties account for several large errors; the three-suburb sample and available features limit the conclusions that can be drawn.
