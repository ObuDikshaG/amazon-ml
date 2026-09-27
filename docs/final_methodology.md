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



\## 5. Error Analysis



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

