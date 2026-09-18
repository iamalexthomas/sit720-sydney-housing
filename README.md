# SIT720 Task 8.1D - Sydney housing prices

Beginner-style worked project using 119 real sold-property records: Parramatta 37, Blacktown 43, Mosman 39. The notebook compares KNN, a decision tree and random forest with five-fold cross-validation. It keeps 24 properties out of training and shows the five largest errors.

## Before submitting

Before submitting, note these limitations:

1. The student supplied all ten personal estimates. They were supplied after actual prices and AI examples had been shown, so they are labelled **non-blind student estimates**. The comparison is complete as a descriptive table, but it does not demonstrate independent human forecasting. `data/student_estimate_protocol.md` records the conditions.
2. The standalone GenAI acknowledgement was removed at the student's request. The task sheet asks for an acknowledgement, so this requirement is currently unmet.

Review the analysis and sources and understand the code. `NOTES_GUIDE.md` connects the project to every supplied notes screenshot and provides viva questions. The student's own reflections and data verification are still important.

## Files

- `SIT720_8_1D.ipynb`: notebook with executed cells, tables and plots.
- `output/pdf/SIT720_8_1D_report.pdf`: concise report with plots, error cases, comparison, screenshots, references and code extracts.
- `data/housing_sales.csv`: real listing-reported sold-property facts, sources and dates.
- `data/collection_log.md`: collection method, exclusions, inconsistencies and biases.
- `data/comparison_blind.csv`: original features and student-supplied estimate column; historical filename, non-blind estimates.
- `data/llm_estimates.csv`: predictions frozen before selected prices were revealed.
- `data/illustrative_estimates.csv`: AI-generated demonstration values requested by the student; NOT human estimates.
- `train.py`: Python equivalent of the notebook's code cells.
- `stable_knn.py`: deterministic equal-distance tie handling for KNN.
- `model/housing_model.joblib`: selected pipeline trained only on development data.
- `app.py`, `prediction.py`: small Flask app and Python prediction endpoint.
- `site/dist/`: browser app, exported model and local JavaScript inference.
- `results/`, `figures/`: computed outputs, charts and genuine app screenshots.
- `failure_analysis.md`: detailed discussion of the five largest held-out errors.

## Setup and reproduce

Tested using Python 3.14 on Linux. In a terminal, enter the extracted project folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python train.py
python export_model.py
python build_report.py
```

On Windows, activate with `.venv\Scripts\activate`. For the notebook, open `SIT720_8_1D.ipynb` in VS Code/Jupyter using this environment, then Restart Kernel and Run All. Install JupyterLab if no notebook editor is already available: `python -m pip install jupyterlab`, then `jupyter lab`. Run from this project folder. Paths are relative; no live web requests or paid API keys are needed for analysis or prediction.

The split seed is 42. Ten preselected comparison cases plus 14 additional seeded cases form the test set. All imputation, scaling and category encoding are fitted within the five CV folds. Hyperparameters and model choice use development CV only. The selected model remains trained on 95 examples; it is not refitted on test labels. A tie-handling consistency fix was made during deployment verification, after initial evaluation, without optimising test performance. Results shown are for that final consistent implementation.

## Run and use the app

```bash
python app.py
```

Open `http://127.0.0.1:5000`. Choose suburb/type, enter bedrooms, bathrooms, parking and a date, then click **Predict price**. Zero bedrooms means studio; blank parking means unknown. Example: Parramatta, Apartment, 2 bedrooms, 2 bathrooms, 1 parking, 1 August 2026 gives approximately **$692,333**. The app rounds only the displayed result. It warns about dates outside training coverage and rejects unsupported suburbs and invalid counts.

The HTML page runs the exported KNN pipeline locally in the browser. The Flask version also exposes `POST /api/predict` for JSON input using the original Python model. The browser and Python predictions were checked for equality across all collected rows. `verify_project.py` repeats meaningful data, inference and endpoint checks and requires Node.js to run the JavaScript comparison.

A build-free alternative is `python -m http.server 8000 --directory site/dist`, then open `http://127.0.0.1:8000`. Do not double-click index.html because the browser must load model.json through HTTP. Host the entire `site/dist` directory on a static host to deploy the browser version. It needs no Python server or API key on the host.

Hosted application: https://iamalexthomas.github.io/sit720-sydney-housing/

Dataset and source repository: https://github.com/iamalexthomas/sit720-sydney-housing

The GitHub Pages application is public. The repository includes the dataset, executed notebook, model, source and PDF, and provides the accessible GitHub alternative requested in the task sheet.

## Rebuild the report and ZIP

Set the actual application/archive URLs in `submission_links.json`, then run:

```bash
python build_report.py
python package_submission.py
```

The ZIP contains source, dataset, model, executed notebook, outputs and report, and excludes virtual environments, temporary browsing returns and Git credentials. If changing data, retrain and rerun the notebook first. If a different model wins, the KNN-only browser exporter will stop with a clear error rather than silently deploy a different algorithm.

## Limitations

The data are an AI-assisted manual transcription of public listing cards, not independently verified settlement data. Advertised area is mixed and excluded from modelling. Suburb, type and sale date are confounded, buildings can appear across splits, and the convenience comparison sample includes rare luxury homes. Test MAE is about $1.20 million; this is an educational prototype, not a professional valuation or lending tool.

## GitHub Pages

A ready-to-run deployment workflow is included at `.github/workflows/pages.yml`. See `GITHUB_PAGES.md` for the repository layout and setup. The workflow publishes the static predictor from `site/dist`.
