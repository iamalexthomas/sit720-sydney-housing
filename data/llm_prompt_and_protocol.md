# LLM estimate record

Date: 16 September 2026. Model: Codex assistant in this conversation; exact underlying model identifier is not supplied by the interface. No separate API model call or claimed independent human was used.

Task: Estimate a sale price in Australian dollars for each row of comparison_blind.csv using only suburb, property type, bedrooms, bathrooms, parking and sale date. A blank parking count means unknown. Treat bedrooms=0 as a studio. Do not look up the property, use its address or advertised area, inspect its actual price, or use ML predictions. Return one estimate and a short reason for each row.

The ten estimates were recorded before the selected targets were unmasked and before model fitting. Tool-output filtering hid all prices on their source pages. The selected records were checked against previously viewed addresses to avoid known targets. Earlier examples from the three markets were available in conversation, so this is a contextual LLM estimate, not a fresh-session experiment. General training-data memorisation cannot be ruled out. The human receives the same feature table. Engineered features are deterministic transformations of these inputs.

Selection: two previously unseen Parramatta records, the first four eligible Blacktown page-3 records, and the first four previously unseen Mosman house records with disclosed prices. This is a convenience comparison with extra houses, not a random benchmark of Sydney.

Human estimates remain blank until the student supplies them. Do not replace them with an algorithm or another LLM and call them human judgement.

## User-requested illustrative estimates

The student asked the assistant to make its own data instead of providing personal estimates. `illustrative_estimates.csv` therefore contains explicitly AI-generated, rounded demonstration values. They were added after outcomes were available and are NOT a blinded human experiment. Their errors may be calculated to demonstrate the table, but they cannot support a conclusion about human skill. The original `human_estimate_aud` column stays empty. The task's genuine human-judgement requirement remains unmet.
