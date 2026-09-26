import pandas as pd

gt = pd.read_csv(
    "dataset/train/train_ground_truth.tsv",
    sep="\t"
)

print("Total ground truth rows:", len(gt))

gt_valid = gt.dropna(
    subset=["matched_entity_ids"]
).copy()

print("Rows with valid matches:", len(gt_valid))

gt_valid["match_count"] = (
    gt_valid["matched_entity_ids"]
    .astype(str)
    .str.split(",")
    .str.len()
)

print("\nMatch statistics:")
print(gt_valid["match_count"].describe())

print("\nSample ground-truth records:")
print(
    gt_valid[
        ["source1_entity_id", "matched_entity_ids"]
    ].head(10).to_string(index=False)
)

source1_ids = set(
    gt_valid["source1_entity_id"]
)

print("\nUnique Source1 IDs in ground truth:")
print(len(source1_ids))