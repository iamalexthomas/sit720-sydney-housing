# Verification record

Checked on 17 September 2026 using the versions in requirements.txt.

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

Known handover gaps: no genuine human estimates, no externally shared archive URL, and the app currently requires owner sign-in. See README.md before submission. Generated illustrative estimates do not satisfy the task's personal-estimate requirement.
