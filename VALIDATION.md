# Verification record

Rechecked on 18 September 2026 using the versions in requirements.txt.

- 119 distinct sold-property rows; all three suburbs have at least 30 rows.
- All 119 transcriptions matched the viewed source-card text. Source provenance and ambiguities are recorded in data/collection_log.md. This checks transcription, not independent settlement records.
- 95 development and 24 test rows, with all ten comparison cases held out.
- Final notebook: all 15 code cells executed, saved outputs, no error outputs.
- Python and JavaScript KNN predictions agree exactly for all 119 recorded inputs.
- Flask page, model file and valid JSON prediction work; missing/invalid inputs return HTTP 400.
- Real browser: form loads, example prediction is $692,333, no observed console errors, desktop and mobile layouts checked. Full screenshots are in figures/.
- Browser did not expose WebMCP; optional WebMCP integration was not end-to-end verified. Ordinary form prediction works without it.
- Sites deployment version 1 succeeded. Visiting the hosted URL from the isolated signed-out browser shows the expected sign-in requirement. Hosted inference was not tested behind authenticated access; equivalent local static assets were tested.
- PDF pages were rendered and visually inspected for layout, table alignment and legibility.
- The ZIP excludes Git history, environment directories, temporary browser extracts and credentials.

Known handover limitation: student estimates were supplied after disclosure of actual prices and AI examples; the standalone GenAI acknowledgement remains removed at student request. The public GitHub repository now supplies the source/data sharing link. See README.md before submission. Generated illustrative estimates do not satisfy the task's personal-estimate requirement.

## GitHub Pages verification - 18 September 2026

- Public repository: https://github.com/iamalexthomas/sit720-sydney-housing
- Public application: https://iamalexthomas.github.io/sit720-sydney-housing/
- GitHub Actions deployment succeeded.
- In an isolated signed-out browser, the page loaded without authentication and the example form returned **$692,333**, with no input errors or observed browser runtime errors.
- The publicly served model.json exactly matched the locally validated model.
- The full notebook was rerun: all 15 code cells completed without error.
- Saved test metrics, top-five failure ordering and held-out comparison membership were independently recomputed and checked.
- Final report: 1,216 narrative words; all eight pages rendered and visually checked; footer and standalone acknowledgement removed as requested.

## Student estimates added - 18 September 2026

The ten user-supplied amounts were copied unchanged. The notebook was rerun and the exact values, three-way comparison metrics and held-out membership were verified. Student MAE is $2,043,000; RMSE is $5,601,330.65; R-squared is 0.26549. The student column is explicitly non-blind because actual prices and AI examples were already disclosed. The fitted model and ML/LLM predictions are unchanged.
