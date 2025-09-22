
Write a Python script that performs the following tasks:

1. Read two JSON files: `data/old_data.json` and `data/new_data.json`.
2. Compare the values from both files for:
   - Main fields:
     `all_items`, `items_missing_P31`, `items_with_0_claims`, `items_with_1_claim`, `total_claims_count`, `total_properties_count`.
   - Properties (e.g., P31, P1433):
     - `property_claims_count`
     - `items_with_property`
     - `unique_qids_count`
     - Nested `qids` values (including specific QIDs and `qids_others`).
3. Calculate the difference (`Diff`) between `new_data` and `old_data` for each value:
   - Positive differences should be formatted like `+123`.
   - Negative differences should be formatted like `-123`.
   - No change should be marked as `-`.
4. Generate a text file named `wikitext.txt` and write the output using **Wikitext table format** exactly like the provided example in file `data/wikitext_sample.txt`.
5. Ensure the script:
   - Uses the report date from `data/new_data.json`.
   - Preserves the same order and structure as shown in the example.
   - Includes sections for each property (e.g., `== {{P|P31}} ==`, `== {{P|P1433}} ==`) with their respective tables.
