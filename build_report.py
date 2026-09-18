"""Build the report from the saved results and screenshots."""
from pathlib import Path
import json, re
from xml.sax.saxutils import escape
import pandas as pd
from PIL import Image as PILImage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output/pdf'
OUT.mkdir(parents=True, exist_ok=True)
links = json.loads((ROOT / 'submission_links.json').read_text())
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body', fontName='Helvetica', fontSize=10.3, leading=14, spaceAfter=9))
styles.add(ParagraphStyle(name='SmallText', fontName='Helvetica', fontSize=8.2, leading=11, spaceAfter=7))
styles.add(ParagraphStyle(name='CodeSmall', fontName='Courier', fontSize=7.4, leading=9.4, spaceAfter=8))
styles['Heading1'].fontSize = 17
styles['Heading1'].leading = 21
styles['Heading1'].textColor = colors.HexColor('#174e70')
styles['Heading2'].fontSize = 12
styles['Heading2'].leading = 15
story = []
narrative = []
def heading(text): story.append(Paragraph(escape(text), styles['Heading1']))
def sub(text): story.append(Paragraph(escape(text), styles['Heading2']))
def para(text, small=False, count=True):
    story.append(Paragraph(text, styles['SmallText' if small else 'Body']))
    if count: narrative.append(re.sub('<[^>]*>', '', text))
def page(): story.append(PageBreak())
def figure(name, width=490, caption=''):
    path = ROOT / 'figures' / name
    w,h = PILImage.open(path).size
    story.append(Image(str(path), width=width, height=width*h/w))
    if caption: para(caption, small=True, count=False)
def table(headers, rows, widths):
    cells = [[Paragraph(escape(str(x)), styles['SmallText']) for x in headers]]
    cells += [[Paragraph(escape(str(x)), styles['SmallText']) for x in row] for row in rows]
    t = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6eef4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.grey),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#dddddd')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    story.append(t); story.append(Spacer(1,8))
def code(text): story.append(Preformatted(text.strip(), styles['CodeSmall']))
def money(x): return f'${x:,.0f}'
def csv(name): return pd.read_csv(ROOT / 'results' / name)
def link(url, label): return f'<link href="{escape(url, {chr(34): "&quot;"})}" color="#175b8a">{escape(label)}</link>'

heading('Sydney housing price prediction')
para('SIT720 Task 8.1D | 18 September 2026', small=True, count=False)
sub('1. Problem and data collection')
para('This project evaluates regression methods for predicting residential sale prices in Australian dollars. Parramatta, Blacktown and Mosman were selected as contrasting purchasing locations. The Parramatta sample consists mainly of apartments, Blacktown includes houses and apartments, and Mosman contains higher-priced properties. These differences allow the analysis to examine how location, dwelling type and accommodation relate to sale prices.')
para('The dataset contains 119 sold properties: 37 in Parramatta, 43 in Blacktown and 39 in Mosman. Sale information was transcribed from Domain and realestate.com.au listings accessed on 16 September 2026. Each record includes its source URL and access date to support traceability. The reported prices are listing information rather than independently verified settlement records.')
table(['Recorded fields', 'Use'], [['Sale price (AUD)', 'Prediction target'],['Suburb, type, bedrooms, bathrooms, parking, sale date','Model inputs'],['Address, advertised area, source, access date, property ID','Checking and traceability; excluded from prediction']], [250,240])
para('Collection problems included withheld prices, missing parking, inconsistent area definitions and changing listing details. Withheld-price and retirement listings were excluded. Missing parking stays unknown. Advertised area is retained for checking but excluded because it mixes land, floor and whole-building area. All 119 transcriptions were checked against the viewed listing text; this does not independently verify settlement records.')
para('The sample is convenient rather than random. Disclosed prices may be selective, several units share buildings, and the Mosman house search was supplemented separately. Results should not be presented as official suburb statistics or as reliable estimates for all Sydney properties.')
sub('Data and implementation')
app_url=links.get('application_url','')
archive_url=links.get('archive_url','')
on_github_pages = '.github.io/' in app_url
app_label = 'Open the housing predictor on GitHub Pages' if on_github_pages else 'Open the deployed housing predictor (owner-private)'
para('Application: '+ (link(app_url,app_label) if app_url else 'See README for local launch.'), count=False)
para('Dataset and source archive: '+ (link(archive_url,'Open the submission archive') if archive_url else '<b>Accessible archive URL not yet supplied.</b> Upload the included ZIP to OneDrive/Dropbox or GitHub and add its link in submission_links.json, then rebuild this report.'), small=True, count=False)

page(); heading('2. Understanding and preparing the data')
para('A fixed split reserves 24 test properties: ten preselected comparison cases and fourteen additional cases sampled by suburb with seed 42. The remaining 95 support exploration and model selection. The test is not purely random, and nearby units can cross the split. Building-grouped and forward-time tests would be stronger.')
figure('price_distribution.png',caption='Figure 1. Development data only. The right tail contains expensive Mosman houses.')
para('Development median prices are $572,000 in Parramatta, $854,000 in Blacktown and $2,152,500 in Mosman. Prices are right-skewed. Expensive genuine sales are retained; removing them would conceal important failures.')
figure('time_and_bedrooms.png',caption='Figure 2. Sale dates and bedrooms. Older observations are mainly Mosman homes.')
para('The date plot cannot establish a market trend because suburb and property mix change over time. Before engineering, the expected three strongest inputs were suburb, property type and bedrooms: market location, dwelling form and accommodation. Month index and bathrooms per bedroom were then added without using prices; studios use a denominator of one.')
para('Within each cross-validation fold, missing numeric inputs use the training median, numeric features are standardised, and categories are one-hot encoded. This prevents preprocessing leakage. Scaling is essential for distance-based KNN. Address and listing identifiers are excluded.')

page(); heading('3. Model development and evaluation')
para('Three regression approaches were selected: KNN for similarity-based prediction, a decision tree for interpretable nonlinear rules, and random forest for variance reduction through averaging. Random forest was expected to perform best before training, although its predictions are less transparent than a single tree. Five shuffled folds evaluate a small parameter grid using MAE. RMSE emphasises large errors, while R-squared measures performance relative to a mean-price baseline.')
cv=csv('cross_validation.csv')
table(['Model', 'CV MAE', 'CV RMSE', 'CV R²', 'Train MAE'],[[r.model,money(r.cv_mae),money(r.cv_rmse),f'{r.cv_r2:.3f}',money(r.train_mae)] for r in cv.itertuples()], [96,100,100,70,124])
para('Table 1. Mean fold scores at selected settings: KNN k=3; tree unrestricted depth/minimum leaf 3; forest 200 trees, unrestricted depth, minimum leaf 2 and max_features=0.8. KNN k=3/5/9, tree depth 2/4/unrestricted and forest depth 4/unrestricted were tested.',small=True,count=False)
figure('complexity.png',caption='Figure 3. Training and validation MAE at each tested model complexity.')
para('KNN achieved the lowest cross-validation MAE ($437,074), contrary to the initial expectation. Its $16,946 advantage over random forest is small relative to fold variability (SD $207,485 and $156,428, respectively). Increasing k raised training and validation errors, indicating excessive smoothing. Greater tree depth improved both scores within the tested range, although generalisation gaps remained. Fold-level R-squared was unstable because the small folds had different price variances.')
test=csv('test_metrics.csv')
table(['24-property test','MAE','RMSE','R²'],[[r.model,money(r.mae),money(r.rmse),f'{r.r2:.3f}'] for r in test.itertuples()], [145,115,125,105])
para('KNN outperformed the median baseline on the test set, but its large absolute errors limit practical use. Random forest obtained slightly lower test MAE and the tree lower RMSE. The cross-validation selection was retained to avoid choosing a model using test outcomes. Because cross-validation also guided tuning, its reported scores may be optimistic. KNN was retained for deployment on this basis.')

page(); heading('4. Investigating the five largest errors')
f=csv('five_largest_errors.csv')
table(['Property', 'Actual', 'KNN estimate', 'Absolute error'],[[r.address,money(r.sale_price_aud),money(r.predicted_price_aud),money(abs(r.predicted_price_aud-r.sale_price_aud))] for r in f.itertuples()], [185,100,100,105])
para('<b>17 Morella Road, Mosman:</b> the $23 million luxury sale exceeds the highest training price ($11.55 million). Neighbour averaging cannot reach it. Harbour views, architectural design and bay access are missing. The retained sold-card bathroom count is three; a current profile says four. [4]')
para('<b>10 Cyprian Street, Mosman:</b> views, a pool and rebuilding potential are absent. Its encoded inputs match Morella exactly, including March 2026, so both receive $5.391 million despite very different outcomes. [5]')
para('<b>53-53A Pelleas Street, Blacktown:</b> seven bedrooms and four bathrooms attract inappropriate neighbours: two Mosman houses at $9 million and $3.9 million, alongside a $1.5 million local house. The model misses the local context of this dual-living home. [6]')
para('<b>96 Glover Street, Mosman:</b> the listing reports a 379 m² block, shared driveway and $3,600 quarterly strata charges. These omitted details could help explain the overestimate. One neighbour costs $8.7 million. This is a plausible explanation, not a proven causal effect. [7]')
para('<b>13 Lancaster Street, Blacktown:</b> a recent custom-built, multigenerational house is compared with three local sales between $1.235 million and $1.34 million. Construction age and finish quality are missing, so its premium is underestimated. [8]')
figure('test_errors.png',width=470,caption='Figure 4. Held-out predictions and errors. Rare, expensive sales dominate squared error.')

page(); heading('5. Comparison of valuation approaches')
para('Ten held-out properties were assessed using the selected KNN model, a large language model (Codex) and personal estimates. The LLM estimates were recorded before the target prices were disclosed, although earlier market examples were available. Personal estimates were recorded after sale prices and reference estimates had been shown; their errors are therefore descriptive rather than evidence of independent forecasting accuracy.')
c=csv('ten_property_comparison.csv')
table(['ID / suburb','Actual','ML','LLM','Personal'],[[r.comparison_id+' / '+r.suburb,money(r.sale_price_aud),money(r.predicted_price_aud),money(r.llm_estimate_aud),money(r.human_estimate_aud)] for r in c.itertuples()], [116,94,94,94,92])
para('Table 3. Sale prices and estimates in AUD. Property identifiers link to the full feature records in the accompanying dataset.',small=True,count=False)
cm=csv('comparison_metrics.csv')
table(['Approach','MAE','RMSE','R²'],[[('Personal estimate' if r.approach == 'Student (non-blind)' else r.approach),money(r.mae),money(r.rmse),f'{r.r2:.3f}'] for r in cm.itertuples()], [145,115,125,105])
para('Under these conditions, personal estimates produced the lowest numerical MAE ($2,043,000) and RMSE ($5,601,331). They were closest for four properties, compared with three each for the LLM and KNN. The personal estimates were particularly close for C06 and C08, while the LLM was closest for C05. All three approaches substantially underestimated the $23 million sale.')
para('The LLM achieved lower MAE than KNN, whereas KNN achieved lower RMSE. Human judgement may contribute inspection findings and local knowledge, but this comparison does not isolate those advantages. KNN is reproducible but constrained by its training data; LLM estimates may be plausible without adequate property-specific evidence. A stronger comparison would record all estimates before disclosing outcomes.')
sub('Revisiting the feature expectations')
para('Validation permutation importance ranks suburb first, then month and bathrooms. The initial guess is partly supported: location leads, but type and bedrooms rank lower. Importance is not causal; correlated features share information, and month may identify the collection pattern rather than price growth.')


page(); heading('6. Deployment and use')
para('The fitted 95-row KNN pipeline is saved with joblib. A Flask endpoint uses that pipeline; a static HTML/JavaScript interface loads exported scaling, imputation, categories and neighbours. Python and browser predictions match for all 119 records. Equal-distance ties use a stable row order in both implementations. This consistency fix followed initial evaluation and did not tune test performance.')
figure('app_input.png',width=410,caption='Figure 5. Property input form before prediction.')
figure('app_prediction.png',width=410,caption='Figure 6. Prediction for a Parramatta apartment: 2 bedrooms, 2 bathrooms, 1 parking space, 1 August 2026.')
access_note = 'The app is publicly hosted on GitHub Pages and requires no sign-in.' if on_github_pages else 'The hosted version is owner-private; tutor access must be arranged separately.'
para('Choose suburb and type, enter room counts, parking and date, then click Predict price. Zero bedrooms means studio; blank parking means unknown. The app displays the estimate, model description and test error. Dates beyond training coverage trigger a warning. ' + access_note,small=True)

page(); heading('Reproduction, reflection and sources')
sub('Build and run')
code('''python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python train.py
python export_model.py
python verify_project.py
python build_report.py
python app.py''')
para('Use the extracted project folder. On Windows activate with .venv\\Scripts\\activate. Open http://127.0.0.1:5000. For notebook outputs, select this environment in Jupyter/VS Code and run all cells. The static folder site/dist can also be hosted directly. Verification needs Node.js. Full setup and archive instructions are in README.md.',small=True,count=False)
sub('Reflection')
para('The main finding is that data coverage and feature quality constrain performance more than model complexity alone. Random forest did not achieve the expected advantage, and KNN\'s favourable cross-validation result did not prevent large test errors. Missing information about area, views, condition and ownership costs limits the relationships available to each model. Further work should prioritise consistent property details, building-grouped splits and forward-time evaluation.')
para('Deployment required identical preprocessing and distance tie handling in Python and JavaScript. A simple interface makes the prediction process accessible, but additional computing alone cannot compensate for missing information. Suburb may reflect historic inequality, while selective disclosure may underrepresent particular housing types. Test MAE was $100,278 for Parramatta, $504,389 for Blacktown and $2,636,093 for Mosman. With only six to nine cases per group, these results cannot establish fairness or justify lending decisions.')
sub('References (accessed 16–17 September 2026)')
refs=[
('1. SIT720 supplied task sheet and all Week 8/9 note screenshots',''),
('2. Domain sold listings: Parramatta and Blacktown; exact page URLs in housing_sales.csv','https://www.domain.com.au/sold-listings/parramatta-nsw-2150/'),
('3. realestate.com.au sold listings: Mosman; exact page URLs in housing_sales.csv','https://www.realestate.com.au/sold/in-nsw-mosman/list-1'),
('4. Morella Road sold listing','https://www.realestate.com.au/sold/property-house-nsw-mosman-149267976'),
('4a. Morella Road current profile (bathroom discrepancy)','https://www.domain.com.au/property-profile/17-morella-road-mosman-nsw-2088'),
('5. Cyprian Street sold listing','https://www.realestate.com.au/sold/property-house-nsw-mosman-150397796'),
('6. Pelleas Street sold listing','https://www.domain.com.au/53-53a-pelleas-street-blacktown-nsw-2148-2020916590'),
('7. Glover Street sold listing','https://www.realestate.com.au/sold/property-house-nsw-mosman-150415760'),
('8. Lancaster Street sold listing','https://www.domain.com.au/13-lancaster-street-blacktown-nsw-2148-2021028342'),
('9. scikit-learn: cross-validation','https://scikit-learn.org/stable/modules/cross_validation.html'),
('10. scikit-learn: leakage and common pitfalls','https://scikit-learn.org/stable/common_pitfalls.html'),
('11. scikit-learn: ensemble methods','https://scikit-learn.org/stable/modules/ensemble.html')]
for label,url in refs: para(link(url,label) if url else escape(label), small=True,count=False)

page(); heading('Appendix: core code')
para('Core steps adapted from train.py. The executed notebook and all source files in the archive contain the complete workflow, outputs, plots and application. See stable_knn.py for deterministic tie handling.',small=True,count=False)
# Use compact, faithful extracts rather than shrinking the full notebook to unreadable text.
code('''def make_features(frame):
    features = frame[["suburb", "property_type", "bedrooms",
                      "bathrooms", "parking"]].copy()
    dates = pd.to_datetime(frame["sale_date"])
    features["sale_month"] = (dates.dt.year - 2025) * 12 + dates.dt.month - 1
    features["bathrooms_per_bedroom"] = (
        features["bathrooms"] / features["bedrooms"].clip(lower=1))
    return features

numeric = ["bedrooms", "bathrooms", "parking", "sale_month",
           "bathrooms_per_bedroom"]
categorical = ["suburb", "property_type"]
preprocess = ColumnTransformer([
    ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                      ("scale", StandardScaler())]), numeric),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
     categorical)
])
cv = KFold(n_splits=5, shuffle=True, random_state=42)

# Example: KNN selection. The notebook repeats this for all models.
pipe = Pipeline([("preprocess", preprocess),
                 ("model", StableKNNRegressor())])
search = GridSearchCV(pipe, {"model__n_neighbors": [3, 5, 9]},
    scoring={"mae": "neg_mean_absolute_error",
             "rmse": "neg_root_mean_squared_error", "r2": "r2"},
    refit="mae", cv=cv, return_train_score=True)
search.fit(X_train, y_train)

predictions = best_model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)
joblib.dump(best_model, ROOT / "model/housing_model.joblib")''')
para('The appendix abbreviates variable setup and the model loop; run the notebook or train.py for a complete runnable program. The saved pipeline includes preprocessing, preventing separate application transformations from drifting away from training.',small=True,count=False)
sub('Application structure')
table(['File','Responsibility'],[['app.py','Serve the page and POST /api/predict'],['prediction.py','Validate input, engineer features and call Python pipeline'],['export_model.py','Export fitted KNN preprocessing and neighbour data'],['site/dist/predict.js','Apply the same transformations and stable KNN average'],['site/dist/app.js','Read the form, validate and display result'],['verify_project.py','Check data, held-out split, API and Python/JavaScript parity']], [160,330])

doc=SimpleDocTemplate(str(OUT/'SIT720_8_1D_report.pdf'), pagesize=A4, rightMargin=48,leftMargin=48,topMargin=40,bottomMargin=42, title='SIT720 8.1D - Sydney housing prices',author='SIT720 project')
doc.build(story)
words=len(' '.join(narrative).split())
(ROOT/'results/report_word_count.txt').write_text(f'Approximate narrative word count: {words}\nExcludes tables, figure captions, code, references and setup instructions.\n')
print('Report created:',OUT/'SIT720_8_1D_report.pdf')
print('Approximate narrative words:',words)
