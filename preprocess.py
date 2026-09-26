import pandas as pd
import re
import unicodedata


def normalize_text(value):
    """Normalize text while preserving non-English characters."""

    if pd.isna(value):
        return ""

    value = str(value)

    # Unicode normalization
    value = unicodedata.normalize("NFKC", value)

    # Convert to lowercase
    value = value.lower()

    # Replace punctuation and symbols with spaces
    value = re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE)

    # Remove extra whitespace
    value = re.sub(r"\s+", " ", value).strip()

    return value


def preprocess_chunk(chunk):
    """Add normalized columns without changing original data."""

    chunk["business_name_normalized"] = (
        chunk["business_name"].apply(normalize_text)
    )

    chunk["business_address_normalized"] = (
        chunk["business_address"].apply(normalize_text)
    )

    chunk["country_normalized"] = (
        chunk["country"].apply(normalize_text)
    )

    return chunk


if __name__ == "__main__":

    input_files = [
        "dataset/train/train_source1.tsv",
        "dataset/train/train_source2.tsv",
        "dataset/train/train_source3.tsv",
    ]

    for input_file in input_files:

        output_file = input_file.replace(
            ".tsv",
            "_preprocessed.tsv"
        )

        print("\nProcessing:", input_file)

        first_chunk = True

        for chunk in pd.read_csv(
            input_file,
            sep="\t",
            chunksize=100000
        ):

            chunk = preprocess_chunk(chunk)

            chunk.to_csv(
                output_file,
                sep="\t",
                index=False,
                mode="w" if first_chunk else "a",
                header=first_chunk
            )

            first_chunk = False

            print("Processed", len(chunk), "rows")

        print("Finished:", output_file)