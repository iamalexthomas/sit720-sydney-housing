# Task-sheet audit - 18 September 2026

Checked against SIT720-8.1D-1.pdf. The scope is an educational housing-price prediction project, not a professional valuation tool.

| Requirement | Evidence | Status |
| --- | --- | --- |
| Three contrasting Sydney suburbs considered by student | Student confirmed Parramatta, Blacktown and Mosman; report Part 1 | Done |
| At least 100 sold properties, at least 30 per suburb | housing_sales.csv: 119 rows; 37 / 43 / 39 | Done |
| Manual collection, features, prices and sources | AI-assisted manual transcription; source URL/access date per row; collection_log.md | Done, with provenance disclosed |
| Dataset quality, missing values, collection bias | Report Part 1 and notebook | Done |
| Price distributions, suburb differences, time and outliers | Report Part 2; development-only plots and tables in notebook | Done |
| Predict three strongest inputs before engineering | analysis_plan.md; suburb, type, bedrooms | Done |
| Engineer and justify features | Month index and bathrooms/bedroom ratio; leakage-safe preprocessing | Done |
| Three approaches and pretraining expectation | KNN, decision tree, random forest; expected forest | Done |
| k-fold CV and regression metrics | Five folds; MAE, RMSE, R-squared; saved CSV tables | Done |
| Complexity, under/overfit, revisit expectations, recommendation | Report Part 3, complexity plots and notebook interpretation | Done |
| Five largest errors with case investigations | Report Part 4; failure_analysis.md and neighbour audit | Done |
| Ten held-out ML and LLM estimates using matching inputs | IDs C01-C10, frozen LLM estimates, protocol and comparison | Done |
| Student's own ten price estimates | No genuine personal estimates supplied; AI illustrations labelled post-hoc | INCOMPLETE: cannot treat generated guesses as human evidence |
| Compare actual, ML, LLM and human outcomes | ML/LLM metrics and discussion complete; human ranking unavailable | PARTIAL: depends on genuine personal estimates |
| Web app accepting features and returning learned-model prediction | Flask/local browser implementation; GitHub Pages workflow | Done; public Pages prediction verified |
| App screenshots and build/run/use instructions | Report Part 6, figures, README.md and GITHUB_PAGES.md | Done |
| Workflow reflection, ethics and improvements | Report reflection and notebook | Done; student should review drafted first-person wording |
| Approximately 1,200 narrative words | Report word-count file; code/tables/figures/references excluded | Done |
| PDF with evidence and relevant code | output/pdf/SIT720_8_1D_report.pdf; complete code in linked repository | Done |
| Separate executed notebook with visible outputs | SIT720_8_1D.ipynb, 15 executed code cells | Done |
| Accessible source/data archive or GitHub link in report | https://github.com/iamalexthomas/sit720-sydney-housing | Done |
| GenAI acknowledgement | Standalone acknowledgement removed as explicitly requested | INCOMPLETE relative to task sheet |
| Submit through OnTrack | User must submit final report and notebook using their account | Not submitted |

The original ten actual prices are already disclosed. If a properly blinded personal-estimate comparison is required, use ten new unseen properties rather than claiming newly entered values were blind. The report must not claim that the illustrative column measures human performance.

The task sheet lists 18 September 2026 as the feedback deadline and final submission before portfolio submission. Completing files does not itself submit anything to OnTrack.
