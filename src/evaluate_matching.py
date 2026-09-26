import pandas as pd
from matching import match_score


SAMPLE_SIZE = 1000
THRESHOLD = 0.75


def main():
    print("Loading sample data...")

    source1 = pd.read_csv(
        "dataset/train/train_source1_preprocessed.tsv",
        sep="\t",
        nrows=SAMPLE_SIZE
    )

    ground_truth = pd.read_csv(
        "dataset/train/train_ground_truth.tsv",
        sep="\t",
        nrows=SAMPLE_SIZE
    )

    source2 = pd.read_csv(
        "dataset/train/train_source2_preprocessed.tsv",
        sep="\t"
    )

    source3 = pd.read_csv(
        "dataset/train/train_source3_preprocessed.tsv",
        sep="\t"
    )

    source2 = source2.set_index("entity_id")
    source3 = source3.set_index("entity_id")

    total = 0
    correct = 0

    for _, row in source1.iterrows():

        source1_id = row["entity_id"]

        truth = ground_truth[
            ground_truth["source1_entity_id"] == source1_id
        ]

        if truth.empty:
            continue

        matched_ids = truth.iloc[0]["matched_entity_ids"]

        if pd.isna(matched_ids):
            continue

        true_ids = set(str(matched_ids).split(","))

        best_score = 0.0
        best_id = None

        # Check Source 2 true matches
        for entity_id in true_ids:
            if entity_id in source2.index:
                candidate = source2.loc[entity_id]
                score = match_score(row, candidate)

                if score > best_score:
                    best_score = score
                    best_id = entity_id

        # Check Source 3 true matches
        for entity_id in true_ids:
            if entity_id in source3.index:
                candidate = source3.loc[entity_id]
                score = match_score(row, candidate)

                if score > best_score:
                    best_score = score
                    best_id = entity_id

        total += 1

        if best_score >= THRESHOLD:
            correct += 1

    print("\n======================================")
    print("MATCHING EVALUATION")
    print("======================================")
    print("Records evaluated:", total)
    print("Records reaching threshold:", correct)

    if total > 0:
        print(
            "Threshold rate:",
            correct / total
        )


if __name__ == "__main__":
    main()