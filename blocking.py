import pandas as pd
import re
import unicodedata


SAMPLE_SIZE = 10000
CHUNK_SIZE = 100000


def normalize_text(value):
    """Normalize text for blocking."""

    if pd.isna(value):
        return ""

    value = unicodedata.normalize("NFKC", str(value))
    value = value.lower()
    value = re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value).strip()

    return value


def create_name_tokens(value):
    """Create up to three useful name tokens."""

    words = value.split()
    words = [word for word in words if len(word) >= 3]

    return words[:3]


def make_block_keys(name, country):
    """Create blocking keys from business name and country."""

    name = normalize_text(name)
    country = normalize_text(country)

    tokens = create_name_tokens(name)

    return [
        f"{token}|{country}"
        for token in tokens
    ]


def get_candidates(source1_record, source2_index, source3_index):
    """
    Generate Source2 and Source3 candidate IDs
    for one Source1 record.
    """

    candidates2 = set()
    candidates3 = set()

    keys = make_block_keys(
        source1_record["business_name"],
        source1_record["country"]
    )

    for key in keys:
        candidates2.update(
            source2_index.get(key, set())
        )

        candidates3.update(
            source3_index.get(key, set())
        )

    return candidates2, candidates3


def build_block_index(file_path, chunksize=CHUNK_SIZE):
    """
    Build a blocking index from a TSV file.

    Returns:
        index:
            blocking key -> set of entity IDs

        records:
            entity ID -> complete record
    """

    index = {}
    records = {}

    for chunk in pd.read_csv(
        file_path,
        sep="\t",
        chunksize=chunksize
    ):

        for _, row in chunk.iterrows():

            record = row.to_dict()

            entity_id = record.get("entity_id")

            if pd.isna(entity_id):
                continue

            entity_id = str(entity_id)

            records[entity_id] = record

            keys = make_block_keys(
                record.get("business_name", ""),
                record.get("country", "")
            )

            for key in keys:

                index.setdefault(
                    key,
                    set()
                ).add(entity_id)

    return index, records


def evaluate_blocking(
    source1_path,
    source2_path,
    source3_path,
    ground_truth_path,
    sample_size=SAMPLE_SIZE
):
    """
    Evaluate blocking recall on a Source1 sample.
    """

    print("Loading Source 1...")

    source1 = pd.read_csv(
        source1_path,
        sep="\t",
        nrows=sample_size
    )

    ground_truth = pd.read_csv(
        ground_truth_path,
        sep="\t"
    )

    print("\nBuilding Source 2 index...")

    source2_index, _ = build_block_index(
        source2_path
    )

    print("Source 2 index built.")

    print("\nBuilding Source 3 index...")

    source3_index, _ = build_block_index(
        source3_path
    )

    print("Source 3 index built.")

    source2_found = 0
    source3_found = 0

    total_source2_candidates = 0
    total_source3_candidates = 0

    evaluated = 0

    for _, row in source1.iterrows():

        source1_id = row["entity_id"]

        candidates2, candidates3 = get_candidates(
            row,
            source2_index,
            source3_index
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

        source2_true_ids = {
            entity_id
            for entity_id in true_ids
            if entity_id.startswith("S2-")
        }

        source3_true_ids = {
            entity_id
            for entity_id in true_ids
            if entity_id.startswith("S3-")
        }

        if source2_true_ids.intersection(candidates2):
            source2_found += 1

        if source3_true_ids.intersection(candidates3):
            source3_found += 1

    print("\n======================================")
    print("BLOCKING EVALUATION")
    print("======================================")

    print("Source 1 sample:", sample_size)
    print("Source 1 records evaluated:", evaluated)

    if sample_size > 0:

        print(
            "\nAverage Source 2 candidates:",
            total_source2_candidates / sample_size
        )

        print(
            "Average Source 3 candidates:",
            total_source3_candidates / sample_size
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


if __name__ == "__main__":

    evaluate_blocking(
        "dataset/train/train_source1.tsv",
        "dataset/train/train_source2.tsv",
        "dataset/train/train_source3.tsv",
        "dataset/train/train_ground_truth.tsv"
    )