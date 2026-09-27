\# Solution Documentation



\## 1. Solution Overview



The solution performs entity matching between Source 1 and entities from Source 2 and Source 3.



The pipeline consists of preprocessing, blocking, candidate generation, candidate pre-filtering, pairwise feature extraction, Logistic Regression classification, threshold-based matching, and final output generation.



\## 2. Preprocessing



Text fields are normalized using Unicode-aware NFKC normalization.



For business names, addresses, and countries:



\- Convert text to lowercase.

\- Replace punctuation and symbols with spaces.

\- Collapse repeated whitespace.

\- Preserve the original values while storing normalized values separately.



Large datasets are processed in chunks to reduce memory usage.



\## 3. Blocking and Candidate Generation



Blocking generates a smaller set of candidate records for each Source 1 entity.



The blocking strategy uses:



\- Normalized business name with country.

\- Business-name tokens with country.

\- Pairs of business-name tokens with country.

\- Address tokens with country.

\- Combinations of name tokens, address tokens, and country.



Very large non-exact blocks are restricted to a maximum block size of 5,000 candidates.



\### Blocking Evaluation



| Metric | Result |

|---|---:|

| Source 1 records evaluated | 9,440 |

| Average Source 2 candidates | 3,843.4039 |

| Average Source 3 candidates | 3,452.8327 |

| Source 2 blocking recall | 89.5869% |

| Source 3 blocking recall | 91.2394% |



\## 4. Candidate Pre-filtering



Blocked candidates are ranked using a cheap similarity score based on:



\- Name token Jaccard: 0.60

\- Address token Jaccard: 0.30

\- Exact name match: 0.05

\- Exact address match: 0.03

\- Exact country match: 0.02



The top 50 candidates are retained for the final ML matching stage.



\## 5. Pairwise Features



The final model uses:



\- `name\_sequence`

\- `name\_jaccard`

\- `name\_exact`

\- `address\_sequence`

\- `address\_jaccard`

\- `address\_exact`

\- `country\_exact`

\- `name\_length\_diff`

\- `address\_length\_diff`



\## 6. Machine Learning Model



The final classifier is Logistic Regression.



Features are standardized using `StandardScaler`.



Configuration:



\- `max\_iter = 1000`

\- `class\_weight = balanced`

\- `random\_state = 42`



\## 7. Training and Validation



The documented experiment used:



\- Positive pairs: 16,683

\- Negative pairs: 49,984

\- Total pairs: 66,667

\- Training Source 1 records: 4,000

\- Validation Source 1 records: 1,000



The threshold was evaluated from 0.50 to 1.00.



The selected validation threshold was \*\*0.86\*\*.



| Metric | Result |

|---|---:|

| Macro F0.5 | 0.950537 |

| Precision | 0.985358 |

| Recall | 0.906823 |

| True positives | 3,163 |

| Predicted matches | 3,210 |

| True matches | 3,488 |



These are validation results and are not test-set or leaderboard metrics.



\## 8. Final Inference



The final inference script is `src/final\_inference.py`.



The test Source 1 data is processed in chunks of 5,000 records.



For each Source 1 record:



1\. Generate Source 2 and Source 3 candidates.

2\. Combine the candidates.

3\. Apply the candidate pre-filter.

4\. Retain the Top-50 candidates.

5\. Calculate pairwise features.

6\. Standardize the features.

7\. Predict match probabilities using Logistic Regression.

8\. Select matches with probability >= 0.86.

9\. Restrict predictions to the generated candidate set.



\## 9. Output Files



The final pipeline generates:



\- `output/matching\_results.tsv`

\- `output/candidate\_pairs.tsv`



`matching\_results.tsv` contains:



\- `source1\_entity\_id`

\- `matched\_entity\_ids`



`candidate\_pairs.tsv` contains:



\- `source1\_entity\_id`

\- `candidate\_entity\_ids`



The candidate file records the Top-50 candidates passed to the final ML matching stage.



\## 10. Scalability



Large TSV files are processed in chunks.



Blocking indexes are built incrementally, and large non-exact blocks are restricted to control candidate volume.



No separate runtime scalability benchmark is reported.



\## 11. Limitations



Blocking does not provide complete candidate recall.



On the evaluated Source 1 sample:



\- Source 2 blocking recall: 89.5869%

\- Source 3 blocking recall: 91.2394%



A true match that is not included in the candidate set cannot be recovered by the downstream ML model.



The reported ML metrics are validation results from the documented experiment.



The final test data does not have ground-truth labels available for calculating test-set precision, recall, or Macro F0.5.



France-specific open-set handling was not separately validated as an independent component.



\## 12. Final Submission Checks



Before submission, verify:



\- Every test Source 1 entity appears exactly once.

\- Unmatched Source 1 rows have an empty match field.

\- There are no duplicate Source 1 IDs.

\- Every predicted match is present in the final candidate set.

\- `candidate\_pairs.tsv` represents the candidates passed to the final model.

\- The final output contains the required columns.

\- The final output contains the expected number of rows.

