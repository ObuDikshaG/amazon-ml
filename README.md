# Amazon ML Entity Matching

## Project Overview

This project performs entity matching across multiple business data sources.

The pipeline matches records from Source 1 against entities from Source 2 and Source 3 using blocking, candidate generation, pairwise similarity features, and a Logistic Regression classifier.


## Pipeline

The matching pipeline consists of:

1. Text preprocessing
2. Blocking and candidate generation
3. Candidate pre-filtering
4. Pairwise feature extraction
5. Logistic Regression classification
6. Threshold-based matching
7. Top-K candidate selection
8. Output generation


## Blocking and Candidate Generation

Blocking reduces the number of records that need to be compared.

The blocking strategy uses normalized:

- Business names
- Country
- Address tokens
- Combinations of name and address tokens

Very large non-exact blocks are restricted to control candidate volume.

### Blocking Evaluation

| Metric | Result |
|---|---:|
| Source 1 records evaluated | 9,440 |
| Average Source 2 candidates | 3,843.4039 |
| Average Source 3 candidates | 3,452.8327 |
| Source 2 blocking recall | 89.5869% |
| Source 3 blocking recall | 91.2394% |





## Candidate Pre-filtering

After blocking, candidates are ranked using a cheap similarity score based on:

- Name token Jaccard: 0.60
- Address token Jaccard: 0.30
- Exact name match: 0.05
- Exact address match: 0.03
- Exact country match: 0.02

The top 50 candidates are retained for the final ML matching stage.

TOP_K = 50


## Pairwise Features

The final matching model uses the following pairwise features:

- `name_sequence` - Name sequence similarity
- `name_jaccard` - Name token Jaccard similarity
- `name_exact` - Exact normalized name match
- `address_sequence` - Address sequence similarity
- `address_jaccard` - Address token Jaccard similarity
- `address_exact` - Exact normalized address match
- `country_exact` - Exact country match
- `name_length_diff` - Difference in name lengths
- `address_length_diff` - Difference in address lengths


## Machine Learning Model

The final matching model is Logistic Regression.

Before classification, the pairwise features are standardized using `StandardScaler`.

The model configuration is:

- `max_iter = 1000` 
- `class_weight = balanced` 
- `random_state = 42` 

The final inference pipeline uses a random seed of 42 for reproducibility.


## Training and Validation

The documented ML experiment used:

- Positive pairs: 16,683
- Negative pairs: 49,984
- Total pairs: 66,667
- Training Source 1 records: 4,000
- Validation Source 1 records: 1,000

The matching threshold was evaluated from 0.50 to 1.00.

The selected validation threshold was **0.86**.

Validation results at threshold 0.86:

| Metric | Result |
|---|---:|
| Macro F0.5 | 0.950537 |
| Precision | 0.985358 |
| Recall | 0.906823 |
| True positives | 3,163 |
| Predicted matches | 3,210 |
| True matches | 3,488 |

These are validation results from the documented experiment and are not test-set or leaderboard metrics.


## Final Inference

The final inference script is `src/final_inference.py`.

Run it from the project root:

```powershell
python src/final_inference.py


The test Source 1 data is processed in chunks of 5,000 records.

For each Source 1 record:

1. Blocking generates Source 2 and Source 3 candidates.
2. Candidates are combined.
3. The cheap pre-filter ranks the candidates.
4. The top 50 candidates are retained.
5. Pairwise features are calculated.
6. Features are standardized using `StandardScaler`.
7. Logistic Regression predicts match probabilities.
8. Candidates with probability >= 0.86 are selected.
9. Final matches are restricted to the generated candidate set.


## Input Files

dataset/test/test_source1.tsv
dataset/test/test_source2.tsv
dataset/test/test_source3.tsv

Training pairs:

output/training_pairs_1000.tsv

## Output Files

The final inference pipeline generates:

- `output/matching_results.tsv` - Final predicted matches
- `output/candidate_pairs.tsv` - Top-50 candidate pairs passed to the ML stage

### matching_results.tsv

Columns:

- `source1_entity_id` 
- `matched_entity_ids` 

### candidate_pairs.tsv

Columns:

- `source1_entity_id` 
- `candidate_entity_ids` 

The candidate file records the Top-50 candidates passed to the final ML matching stage.

## Reproducibility

The final inference configuration uses:

- `RANDOM_SEED = 42`
- `THRESHOLD = 0.86`
- `TOP_K = 50`
- `SOURCE1_CHUNK_SIZE = 5000`

Run the inference script from the project root.

## Scalability

Large TSV files are processed in chunks rather than loading the entire Source 1 test dataset into memory.

Blocking indexes are built incrementally and large non-exact blocks are restricted to control candidate generation.

No separate runtime scalability benchmark is reported.

## Limitations

Blocking does not provide complete candidate recall.

On the evaluated Source 1 sample:

- Source 2 blocking recall: 89.5869%
- Source 3 blocking recall: 91.2394%

A true match that is not included in the candidate set cannot be recovered by the downstream ML model.

The reported ML metrics are validation results from the documented experiment.

The final test data does not have ground-truth labels available for calculating test-set precision, recall, or Macro F0.5.

France-specific open-set handling was not separately validated as an independent component.

## Final Submission Checks

Before submission, verify:

- Every test Source 1 entity appears exactly once.
- Unmatched Source 1 rows have an empty match field.
- There are no duplicate Source 1 IDs.
- Every predicted match is present in the final candidate set.
- `candidate_pairs.tsv` represents the candidates passed to the final model.
- The final output contains the required columns.
- The final output contains the expected number of rows.