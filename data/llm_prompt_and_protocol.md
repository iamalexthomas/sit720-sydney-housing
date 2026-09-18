# LLM estimate record

Date: 16 September 2026. Model: Codex assistant in this conversation; exact underlying model identifier is not supplied by the interface. No separate API model call or claimed independent human was used.

Task: Estimate a sale price in Australian dollars for each row of comparison_blind.csv using only suburb, property type, bedrooms, bathrooms, parking and sale date. A blank parking count means unknown. Treat bedrooms=0 as a studio. Do not look up the property, use its address or advertised area, inspect its actual price, or use ML predictions. Return one estimate and a short reason for each row.

The ten estimates were recorded before the selected targets were unmasked and before model fitting. Tool-output filtering hid all prices on their source pages. The selected records were checked against previously viewed addresses to avoid known targets. Earlier examples from the three markets were available in conversation, so this is a contextual LLM estimate, not a fresh-session experiment. General training-data memorisation cannot be ruled out. The human receives the same feature table. Engineered features are deterministic transformations of these inputs.

Selection: two previously unseen Parramatta records, the first four eligible Blacktown page-3 records, and the first four previously unseen Mosman house records with disclosed prices. This is a convenience comparison with extra houses, not a random benchmark of Sydney.

The original human column was blank when the LLM predictions were frozen. The student supplied ten estimates on 18 September after disclosure of prices and AI examples. See `student_estimate_protocol.md` for this non-blind protocol.

## User-requested illustrative estimates

The student asked the assistant to make its own data instead of providing personal estimates. `illustrative_estimates.csv` therefore contains explicitly AI-generated, rounded demonstration values. They were added after outcomes were available and are NOT a blinded human experiment. Their errors may be calculated to demonstrate the table, but they cannot support a conclusion about human skill. These examples are retained separately. The `human_estimate_aud` column now contains the actual student-supplied values, not these illustrative values; that later comparison is non-blind.
