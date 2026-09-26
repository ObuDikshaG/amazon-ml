import pandas as pd

files = [
    "dataset/train/train_source1.tsv",
    "dataset/train/train_source2.tsv",
    "dataset/train/train_source3.tsv",
]

for file in files:
    print("\n" + "=" * 70)
    print(file)
    print("=" * 70)

    total_rows = 0
    missing = None
    duplicate_ids = 0

    for chunk in pd.read_csv(file, sep="\t", chunksize=100000):
        total_rows += len(chunk)

        if missing is None:
            missing = chunk.isna().sum()
        else:
            missing += chunk.isna().sum()

        duplicate_ids += chunk["entity_id"].duplicated().sum()

    print("Rows:", total_rows)
    print("\nMissing values:")
    print(missing)

    print("\nDuplicate entity IDs within chunks:", duplicate_ids)