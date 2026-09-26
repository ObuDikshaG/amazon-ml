import pandas as pd
import re
import unicodedata


SAMPLE_SIZE = 10000
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
    words = [word for word in words if len(word) >= 3]
    return words[:3]


def make_block_keys(name, country):
    name = normalize_text(name)
    country = normalize_text(country)

    tokens = create_name_tokens(name)

    return [
        f"{token}|{country}"
        for token in tokens
    ]


# --------------------------------------------------
# Load Source 1 sample
# --------------------------------------------------

print("Loading Source 1...")

source1 = pd.read_csv(
    "dataset/train/train_source1.tsv",
    sep="\t",
    nrows=SAMPLE_SIZE
)

ground_truth = pd.read_csv(
    "dataset/train/train_ground_truth.tsv",
    sep="\t",
    nrows=SAMPLE_SIZE
)

source1["block_keys"] = source1.apply(
    lambda row: make_block_keys(
        row["business_name"],
        row["country"]
    ),
    axis=1
)


# --------------------------------------------------
# Build Source 2 index using ALL rows
# --------------------------------------------------

print("\nBuilding Source 2 index...")

source2_index = {}
source2_ids = {}

for chunk in pd.read_csv(
    "dataset/train/train_source2.tsv",
    sep="\t",
    chunksize=CHUNK_SIZE
):

    for _, row in chunk.iterrows():

        entity_id = row["entity_id"]

        keys = make_block_keys(
            row["business_name"],
            row["country"]
        )

        source2_ids[entity_id] = keys

        for key in keys:

            source2_index.setdefault(
                key, set()
            ).add(entity_id)

    print("Processed Source 2 chunk")


# --------------------------------------------------
# Build Source 3 index using ALL rows
# --------------------------------------------------

print("\nBuilding Source 3 index...")

source3_index = {}
source3_ids = {}

for chunk in pd.read_csv(
    "dataset/train/train_source3.tsv",
    sep="\t",
    chunksize=CHUNK_SIZE
):

    for _, row in chunk.iterrows():

        entity_id = row["entity_id"]

        keys = make_block_keys(
            row["business_name"],
            row["country"]
        )

        source3_ids[entity_id] = keys

        for key in keys:

            source3_index.setdefault(
                key, set()
            ).add(entity_id)

    print("Processed Source 3 chunk")


# --------------------------------------------------
# Evaluate blocking
# --------------------------------------------------

source2_found = 0
source3_found = 0

total_source2_candidates = 0
total_source3_candidates = 0

evaluated = 0


for _, row in source1.iterrows():

    source1_id = row["entity_id"]

    candidates2 = set()
    candidates3 = set()

    for key in row["block_keys"]:

        candidates2.update(
            source2_index.get(key, set())
        )

        candidates3.update(
            source3_index.get(key, set())
        )

    total_source2_candidates += len(candidates2)
    total_source3_candidates += len(candidates3)

    truth = ground_truth[
        ground_truth["source1_entity_id"]
        == source1_id
    ]

    if len(truth) == 0:
        continue

    matched = truth.iloc[0]["matched_entity_ids"]

    if pd.isna(matched):
        continue

    true_ids = set(
        str(matched).split(",")
    )

    evaluated += 1

    if true_ids.intersection(candidates2):
        source2_found += 1

    if true_ids.intersection(candidates3):
        source3_found += 1


# --------------------------------------------------
# Results
# --------------------------------------------------

print("\n======================================")
print("BLOCKING EVALUATION")
print("======================================")

print("Source 1 sample:", SAMPLE_SIZE)

print("Source 1 records evaluated:", evaluated)

print(
    "\nAverage Source 2 candidates:",
    total_source2_candidates / SAMPLE_SIZE
)

print(
    "Average Source 3 candidates:",
    total_source3_candidates / SAMPLE_SIZE
)

print(
    "\nSource 2 records with at least one true match captured:",
    source2_found
)

print(
    "Source 3 records with at least one true match captured:",
    source3_found
)

if evaluated > 0:

    print(
        "\nSource 2 blocking recall:",
        source2_found / evaluated
    )

    print(
        "Source 3 blocking recall:",
        source3_found / evaluated
    )