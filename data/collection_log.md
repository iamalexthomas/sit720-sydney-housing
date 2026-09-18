# Collection and data quality log

Collected on 16 September 2026 from public Domain and realestate.com.au pages. The assistant read listing cards and transcribed 119 rows. This was not a purchased dataset, bulk scraper or synthetic training dataset. The student selected the three suburbs but did not personally perform this transcription. Verify the records and disclose the AI assistance when submitting.

- Parramatta: 37 rows. Ten disclosed sales from Domain page 1, 25 from realestate.com.au page 2, and two previously unseen Domain page-3 comparison cases.
- Blacktown: 43 rows. Twenty disclosed sales from Domain page 1, 19 from page 2 (one withheld listing excluded), and four previously unseen page-3 comparison cases.
- Mosman: 39 rows. Twenty-three disclosed listings from the general sold page after excluding one retirement-living listing and one listing without a clear numeric price. A house-only page supplied 16 further records, including four blinded comparison cases. Later/older remaining rows were not collected once the quota was met.

Selection is by accessible displayed results, with deliberate supplementation of Mosman houses. It is a convenience sample, not random or population weighted. The site can promote listings and include surrounding suburbs; every retained row explicitly names the selected suburb. Paging and prices can change. No asking price or estimated value was substituted for a sold price. Fields were checked against the fetched source text for every row; transcription_checks.csv records that check. This is a source-transcription check, not independent legal verification of the sale.

Each row has an address, sale date, source results-page URL and access date. Unit/flat/apartment labels are normalised to Apartment. Unknown parking and area remain blank. Date strings are converted to ISO dates; prices are integer AUD. No personal seller or buyer information, photographs or copied marketing descriptions are included.

Advertised area is deliberately excluded from models. It mixes floor, land and possibly entire-block area. In particular 36/2-4 Fourth Avenue reports 3,733 m2 and 1103/5 Second Avenue reports 439 m2. The latter field was present in the later fetched page and was added during verification. The source page for 13 Lancaster Street gives 739 m2 on its results card, versus 739.8 m2 on the detail page. The dataset preserves the card value. None of these area changes affects the fitted model.

17 Morella Road's $23 million result is corroborated by the sold listing and Domain property profile. The sold card gives 3 bathrooms, while the current Domain profile gives 4. The dataset retains 3 from its original sold source, flags the disagreement, and does not silently revise test inputs after evaluation. 10 Cyprian Street's sold listing gives 27 March 2026, while a property-history summary gives 26 March. The dataset follows the sold listing consistently.

The largest sources of bias are price-withholding, suburb/type imbalance (no Parramatta houses were captured), older Mosman house sales, sparse unusual dwellings, and potential building overlap across data splits. Missing condition, usable floor area, views, strata fees, planning potential and sale circumstances limit interpretation. These data are listing-reported observations, not official settlement records.
