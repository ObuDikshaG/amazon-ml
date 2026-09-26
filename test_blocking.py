import pandas as pd
import re
import unicodedata

SAMPLE_SIZE = 1000
CHUNK_SIZE = 100000


def normalize_text(value):
    if pd.isna(value):
        return ""

    value = unicodedata.normalize("NFKC", str(value))
    value = value.lower()
    value = re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value).strip()

    return value


def create_name_tokens(value):
    words = value.split()
    return [word for word in words if len(word) >= 3][:3]


def make_block_keys(name, country):
    name = normalize_text(name)
    country = normalize_text(country)

    tokens = create_name_tokens(name)

    return [
        f"{token}|{country}"
        for token in tokens
    ]


# --------------------------------------------------
# 1. Get actual Source1 IDs from ground truth
# --------------------------------------------------

print("Loading ground truth...")

gt = pd.read_csv(
    "dataset/train/train_ground_truth.tsv",
    sep="\t",
    usecols=["source1_entity_id", "matched_entity_ids"]
)

gt = gt.dropna(subset=["matched_entity_ids"])

# Take 1,000 actual Source1 IDs
gt_sample = gt.sample(
    n=SAMPLE_SIZE,
    random_state=42
)

truth_dict = dict(
    zip(
        gt_sample["source1_entity_id"],
        gt_sample["matched_entity_ids"]
    )
)

print("Ground truth sample:", len(gt_sample))


# --------------------------------------------------
# 2. Find those exact Source1 records
# --------------------------------------------------

print("\nFinding Source1 records...")

source1_records = []

for chunk in pd.read_csv(
    "dataset/train/train_source1.tsv",
    sep="\t",
    chunksize=CHUNK_SIZE
):

    matches = chunk[
        chunk["entity_id"].isin(truth_dict.keys())
    ]

    if len(matches) > 0:
        source1_records.append(matches)

    if sum(len(x) for x in source1_records) >= SAMPLE_SIZE:
        break


source1 = pd.concat(
    source1_records,
    ignore_index=True
)

print(
    "Actual Source1 records found:",
    len(source1)
)


# --------------------------------------------------
# 3. Build Source2 blocking index
# --------------------------------------------------

print("\nBuilding Source2 index...")

source2_index = {}

for chunk in pd.read_csv(
    "dataset/train/train_source2.tsv",
    sep="\t",
    chunksize=CHUNK_SIZE
):

    for _, row in chunk.iterrows():

        keys = make_block_keys(
            row["business_name"],
            row["country"]
        )

        for key in keys:

            source2_index.setdefault(
                key, set()
            ).add(row["entity_id"])

    print("Processed Source2 chunk")


# --------------------------------------------------
# 4. Build Source3 blocking index
# --------------------------------------------------

print("\nBuilding Source3 index...")

source3_index = {}

for chunk in pd.read_csv(
    "dataset/train/train_source3.tsv",
    sep="\t",
    chunksize=CHUNK_SIZE
):

    for _, row in chunk.iterrows():

        keys = make_block_keys(
            row["business_name"],
            row["country"]
        )

        for key in keys:

            source3_index.setdefault(
                key, set()
            ).add(row["entity_id"])

    print("Processed Source3 chunk")


# --------------------------------------------------
# 5. Evaluate blocking recall
# --------------------------------------------------

source2_hits = 0
source3_hits = 0

total_source2_candidates = 0
total_source3_candidates = 0

evaluated = 0


for _, row in source1.iterrows():

    source1_id = row["entity_id"]

    keys = make_block_keys(
        row["business_name"],
        row["country"]
    )

    candidates2 = set()
    candidates3 = set()

    for key in keys:

        candidates2.update(
            source2_index.get(key, set())
        )

        candidates3.update(
            source3_index.get(key, set())
        )

    total_source2_candidates += len(candidates2)
    total_source3_candidates += len(candidates3)

    true_matches = set(
        str(truth_dict[source1_id]).split(",")
    )

    true_source2 = {
        x for x in true_matches
        if x.startswith("S2-")
    }

    true_source3 = {
        x for x in true_matches
        if x.startswith("S3-")
    }

    if true_source2.intersection(candidates2):
        source2_hits += 1

    if true_source3.intersection(candidates3):
        source3_hits += 1

    evaluated += 1


# --------------------------------------------------
# 6. Results
# --------------------------------------------------

print("\n======================================")
print("PROPER BLOCKING EVALUATION")
print("======================================")

print("Records evaluated:", evaluated)

print(
    "\nAverage Source2 candidates:",
    total_source2_candidates / evaluated
)

print(
    "Average Source3 candidates:",
    total_source3_candidates / evaluated
)

print(
    "\nSource2 records with true match captured:",
    source2_hits
)

print(
    "Source3 records with true match captured:",
    source3_hits
)

print(
    "\nSource2 blocking recall:",
    source2_hits / evaluated
)

print(
    "Source3 blocking recall:",
    source3_hits / evaluated
)