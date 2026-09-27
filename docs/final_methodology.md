\# Final Methodology



\## 1. Blocking



Final blocking commit:



`118c9cd` - Improve blocking recall with address keys



Blocking evaluation:



\- Source 1 records evaluated: 9,440

\- Average Source 2 candidates: 3,843.4039

\- Average Source 3 candidates: 3,452.8327

\- Source 2 blocking recall: 89.5869%

\- Source 3 blocking recall: 91.2394%



\## 2. ML Features



The pairwise matching model uses the following features:



\### Business name



\- `name\_exact`

\- `name\_sequence`

\- `name\_token\_jaccard`

\- `name\_length\_similarity`



\### Address



\- `address\_sequence`

\- `address\_token\_jaccard`

\- `address\_length\_similarity`

\- `address\_number\_overlap`



\### Country



\- `country\_exact`



\## 3. Threshold Selection



The matching threshold was selected using the validation set by evaluating thresholds from 0.50 to 1.00.



The selected validation threshold was \*\*0.86\*\*, where the validation Macro F0.5 was:



\- Macro F0.5: \*\*0.950537\*\*

\- Precision: \*\*0.985358\*\*

\- Recall: \*\*0.906823\*\*

\- True positives: \*\*3,163\*\*

\- Predicted matches: \*\*3,210\*\*

\- True matches: \*\*3,488\*\*



The threshold was selected based on the highest validation Macro F0.5 among the evaluated thresholds.



\## 4. Validation Results



The finalized-blocking ML experiment used:



\- Positive pairs: 16,683

\- Negative pairs: 49,984

\- Total pairs: 66,667

\- Training Source1 records: 4,000

\- Validation Source1 records: 1,000



At threshold 0.86:



| Metric | Result |

|---|---:|

| Macro F0.5 | 0.950537 |

| Precision | 0.985358 |

| Recall | 0.906823 |

| True positives | 3,163 |

| Predicted matches | 3,210 |

| True matches | 3,488 |

## 4.1 Preprocessing

Text preprocessing uses Unicode-aware normalization.

For business names, addresses, and countries:

- Unicode text is normalized using NFKC normalization.
- Text is converted to lowercase.
- Punctuation and symbols are replaced with spaces.
- Repeated whitespace is collapsed.
- Normalized values are stored in separate columns while preserving the original data.

Preprocessing is performed in chunks of up to 100,000 rows to avoid loading an entire large dataset into memory at once.

## 4.2 Candidate Generation and Matching

Candidate generation uses multiple blocking keys based on normalized business information.

The blocking strategy combines:

- Exact normalized business name with country.
- Individual business-name tokens with country.
- Pairs of business-name tokens with country.
- Address tokens with country.
- Combinations of business-name tokens, address tokens, and country.

Very large non-exact blocks are restricted using a maximum block size of 5,000 candidates, while exact normalized-name blocks are retained.

The pairwise matching stage uses name, address, and country similarity features, including exact matches, sequence similarity, token Jaccard similarity, length similarity, and numeric overlap in addresses.

## 4.3 Scalability Considerations

The implementation uses chunked TSV processing with chunks of up to 100,000 rows.

Blocking indexes are built incrementally and candidate records are stored by entity ID. Candidate generation also limits large non-exact blocks to control candidate volume.

These implementation choices are intended to reduce memory usage and control candidate generation cost. No separate runtime scalability benchmark is reported here.

## 4.4 Limitations

The blocking stage does not provide complete candidate recall.

On the evaluated Source 1 sample, blocking recall was:

- Source 2: 89.5869%
- Source 3: 91.2394%

Therefore, true matches that are not included in the candidate set cannot be recovered by the downstream matching model.

The reported ML metrics are validation results from the documented experiment and should not be interpreted as test-set or leaderboard performance.

The final test data does not have ground-truth labels available for computing test-set precision, recall, or Macro F0.5.

France-specific open-set handling was not separately validated as an independent component of the pipeline.

## 5. Error Analysis



To be completed after final inference:



\- False positives

\- False negatives

\- Name-only matches

\- Address-only matches

\- Country mismatches

\- Abbreviation/legal-suffix cases



\## 6. Final Submission Checks



\- \[ ] Every test Source1 appears exactly once

\- \[ ] Unmatched Source1 rows have an empty match field

\- \[ ] No duplicate IDs

\- \[ ] Every predicted match is present in the final candidate set

\- \[ ] `candidate\_pairs.tsv` represents the actual candidates fed to the final model

\- \[ ] Final output has the required columns

\- \[ ] Final output has the expected number of rows

