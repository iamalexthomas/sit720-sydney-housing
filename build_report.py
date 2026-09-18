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

heading('SIT720 Task 8.1D: Sydney housing prices')
para('Machine learning mini project | 18 September 2026', small=True, count=False)
sub('1. Problem and data collection')
para('This project predicts a property sale price in Australian dollars. Parramatta, Blacktown and Mosman were selected and confirmed as contrasting buying options. The collected Parramatta sample is mainly apartments, Blacktown mixes houses and apartments, and Mosman includes much more expensive homes. Location, accommodation and property type may therefore affect prices.')
para('The dataset contains 119 sold properties: 37 Parramatta, 43 Blacktown and 39 Mosman. Listing facts were manually transcribed by the AI assistant from Domain and realestate.com.au on 16 September 2026. Every row has a source URL. This is not a claim that the student personally collected or independently verified the sales.')
table(['Recorded fields', 'Use'], [['Sale price (AUD)', 'Prediction target'],['Suburb, type, bedrooms, bathrooms, parking, sale date','Model inputs'],['Address, advertised area, source, access date, property ID','Checking and traceability; excluded from prediction']], [250,240])
para('Collection problems included withheld prices, missing parking, inconsistent area definitions and changing listing details. Withheld-price and retirement listings were excluded. Missing parking stays unknown. Advertised area is retained for checking but excluded because it mixes land, floor and whole-building area. All 119 transcriptions were checked against the viewed listing text; this does not independently verify settlement records.')
para('The sample is convenient rather than random. Disclosed prices may be selective, several units share buildings, and the Mosman house search was supplemented separately. Results should not be presented as official suburb statistics or as reliable estimates for all Sydney properties.')
sub('Submission details')
app_url=links.get('application_url','')
archive_url=links.get('archive_url','')
on_github_pages = '.github.io/' in app_url
app_label = 'Open the housing predictor on GitHub Pages' if on_github_pages else 'Open the deployed housing predictor (owner-private)'
para('Application: '+ (link(app_url,app_label) if app_url else 'See README for local launch.'), count=False)
para('Dataset and source archive: '+ (link(archive_url,'Open the submission archive') if archive_url else '<b>Accessible archive URL not yet supplied.</b> Upload the included ZIP to OneDrive/Dropbox or GitHub and add its link in submission_links.json, then rebuild this report.'), small=True, count=False)
para('<b>Part 5 limitation:</b> genuine personal estimates were not supplied. Requested invented values are labelled AI illustrations. This report does not claim a completed human-performance comparison. This personal-estimate requirement remains incomplete.',small=True,count=False)

page(); heading('2. Understanding and preparing the data')
para('A fixed split reserves 24 test properties: ten preselected comparison cases and fourteen additional cases sampled by suburb with seed 42. The remaining 95 support exploration and model selection. The test is not purely random, and nearby units can cross the split. Building-grouped and forward-time tests would be stronger.')
figure('price_distribution.png',caption='Figure 1. Development data only. The right tail contains expensive Mosman houses.')
para('Development median prices are $572,000 in Parramatta, $854,000 in Blacktown and $2,152,500 in Mosman. Prices are right-skewed. Expensive genuine sales are retained; removing them would conceal important failures.')
figure('time_and_bedrooms.png',caption='Figure 2. Sale dates and bedrooms. Older observations are mainly Mosman homes.')
para('The date plot cannot establish a market trend because suburb and property mix change over time. Before engineering, the expected three strongest inputs were suburb, property type and bedrooms: market location, dwelling form and accommodation. Month index and bathrooms per bedroom were then added without using prices; studios use a denominator of one.')
para('Within each cross-validation fold, missing numeric inputs use the training median, numeric features are standardised, and categories are one-hot encoded. This prevents preprocessing leakage. Scaling is essential for distance-based KNN. Address and listing identifiers are excluded.')

page(); heading('3. Model development and evaluation')
para('KNN averages similar sales but can choose poor comparables. A decision tree learns readable rules but can overfit. Random forest averages many trees but is less transparent. Before training, forest was expected to win because averaging can reduce tree variance and capture interactions. Five shuffled folds compare a small parameter grid using MAE. RMSE highlights large errors; R-squared compares squared error with a mean-price baseline.')
cv=csv('cross_validation.csv')
table(['Model', 'CV MAE', 'CV RMSE', 'CV R²', 'Train MAE'],[[r.model,money(r.cv_mae),money(r.cv_rmse),f'{r.cv_r2:.3f}',money(r.train_mae)] for r in cv.itertuples()], [96,100,100,70,124])
para('Table 1. Mean fold scores at selected settings: KNN k=3; tree unrestricted depth/minimum leaf 3; forest 200 trees, unrestricted depth, minimum leaf 2 and max_features=0.8. KNN k=3/5/9, tree depth 2/4/unrestricted and forest depth 4/unrestricted were tested.',small=True,count=False)
figure('complexity.png',caption='Figure 3. Training and validation MAE at each tested model complexity.')
para('KNN is selected by CV MAE ($437,074), against the initial forest expectation. Its $16,946 advantage is smaller than fold variability (KNN SD $207,485; forest $156,428). Higher k increases both errors, suggesting excessive smoothing. Deeper trees improve both scores here, although training-validation gaps remain. More complexity is not automatically worse. Mean fold R-squared is unstable when small folds have different price variance.')
test=csv('test_metrics.csv')
table(['24-property test','MAE','RMSE','R²'],[[r.model,money(r.mae),money(r.rmse),f'{r.r2:.3f}'] for r in test.itertuples()], [145,115,125,105])
para('KNN improves on the median baseline but test errors are large. Forest has slightly lower test MAE and the tree lower RMSE; the CV choice is retained to avoid selecting on test results. CV scores also served tuning, so they are mildly optimistic. KNN is recommended only for this study prototype.')

page(); heading('4. Investigating the five largest errors')
f=csv('five_largest_errors.csv')
table(['Property', 'Actual', 'KNN estimate', 'Absolute error'],[[r.address,money(r.sale_price_aud),money(r.predicted_price_aud),money(abs(r.predicted_price_aud-r.sale_price_aud))] for r in f.itertuples()], [185,100,100,105])
para('<b>17 Morella Road, Mosman:</b> the $23 million luxury sale exceeds the highest training price ($11.55 million). Neighbour averaging cannot reach it. Harbour views, architectural design and bay access are missing. The retained sold-card bathroom count is three; a current profile says four. [4]')
para('<b>10 Cyprian Street, Mosman:</b> views, a pool and rebuilding potential are absent. Its encoded inputs match Morella exactly, including March 2026, so both receive $5.391 million despite very different outcomes. [5]')
para('<b>53-53A Pelleas Street, Blacktown:</b> seven bedrooms and four bathrooms attract inappropriate neighbours: two Mosman houses at $9 million and $3.9 million, alongside a $1.5 million local house. The model misses the local context of this dual-living home. [6]')
para('<b>96 Glover Street, Mosman:</b> the listing reports a 379 m² block, shared driveway and $3,600 quarterly strata charges. These omitted details could help explain the overestimate. One neighbour costs $8.7 million. This is a plausible explanation, not a proven causal effect. [7]')
para('<b>13 Lancaster Street, Blacktown:</b> a recent custom-built, multigenerational house is compared with three local sales between $1.235 million and $1.34 million. Construction age and finish quality are missing, so its premium is underestimated. [8]')
figure('test_errors.png',width=470,caption='Figure 4. Held-out predictions and errors. Rare, expensive sales dominate squared error.')

page(); heading('5. ML, LLM and illustrative estimates')
para('Ten held-out properties received the same six raw inputs for ML and Codex estimates. LLM answers were frozen before these prices were revealed. Codex had seen earlier market examples, so this was not a fresh-context or equal-training-information experiment. The prompt and protocol are included. Genuine student estimates are missing; the requested invented column was added after outcomes were known.')
c=csv('ten_property_comparison.csv')
table(['ID / suburb','Actual','ML','LLM','AI illustration*'],[[r.comparison_id+' / '+r.suburb,money(r.sale_price_aud),money(r.predicted_price_aud),money(r.llm_estimate_aud),money(r.illustrative_estimate_aud)] for r in c.itertuples()], [116,94,94,94,92])
para('Table 3. *Post-hoc demonstration values, NOT personal estimates or blind predictions. Addresses and inputs are mapped to these IDs in the notebook and CSV files.',small=True,count=False)
cm=csv('comparison_metrics.csv')
table(['Approach','MAE','RMSE','R²'],[[r.approach,money(r.mae),money(r.rmse),f'{r.r2:.3f}'] for r in cm.itertuples()], [145,115,125,105])
para('The LLM has lower MAE, but ML has lower RMSE. Both badly miss the $23 million sale. The LLM is closer for the seven-bedroom Blacktown home; ML is closer for the $5.3 million Mosman home. Neither knows omitted exceptional features. Ten selected cases cannot establish a general winner.')
para('Human judgement could add inspection knowledge, condition and local comparables, but that benefit is not measured here. A valid human comparison now requires new blinded cases. Invented estimates cannot establish whether a person outperforms either model.')
sub('Revisiting the feature expectations')
para('Validation permutation importance ranks suburb first, then month and bathrooms. The initial guess is partly supported: location leads, but type and bedrooms rank lower. Importance is not causal; correlated features share information, and month may identify the collection pattern rather than price growth.')


page(); heading('6. Deployment and use')
para('The fitted 95-row KNN pipeline is saved with joblib. A Flask endpoint uses that pipeline; a static HTML/JavaScript interface loads exported scaling, imputation, categories and neighbours. Python and browser predictions match for all 119 records. Equal-distance ties use a stable row order in both implementations. This consistency fix followed initial evaluation and did not tune test performance.')
figure('app_input.png',width=345,caption='Figure 5. Actual local browser screenshot: choose features before prediction.')
figure('app_prediction.png',width=345,caption='Figure 6. Actual local browser screenshot: Parramatta apartment, 2 bedrooms, 2 bathrooms, 1 parking, 1 August 2026 gives $692,333.')
access_note = 'The app is publicly hosted on GitHub Pages and requires no sign-in.' if on_github_pages else 'The hosted version is owner-private; tutor access must be arranged separately.'
para('Choose suburb and type, enter room counts, parking and date, then click Predict price. Zero bedrooms means studio; blank parking means unknown. The app shows the estimate and study limitations. Dates beyond training coverage trigger a warning. ' + access_note,small=True)

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
para('My main takeaway is that better data matters more than a more complicated model. I expected random forest to perform best, but KNN had the lowest cross-validation MAE. Its large test errors show why I should not rely on one score. Missing area, views, condition and ownership costs limit what the model can learn. I would collect more consistent property details and use building-grouped and time-based tests before trusting it on new sales.')
para('I would keep the app simple so its inputs and limitations are easy to understand. Deploying it also shows why preprocessing must match training exactly. More computing power alone would not fix missing information. Suburb can reflect historic inequality, and selective listings can favour some housing types. Test MAE is about $100,278 for Parramatta, $504,389 for Blacktown and $2,636,093 for Mosman. Each group has only six to nine test cases, so this does not establish fairness. I would avoid using this prototype for lending or decisions about access to housing.')
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
