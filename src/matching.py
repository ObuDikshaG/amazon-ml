import pandas as pd
from difflib import SequenceMatcher


def get_value(record, normalized_column, original_column):
    """
    Use the preprocessed value when available.
    Fall back to the original column if needed.
    """
    if normalized_column in record:
        value = record[normalized_column]
    else:
        value = record[original_column]

    if pd.isna(value):
        return ""

    return str(value).strip().lower()


def similarity(value1, value2):
    """Calculate similarity between two text values."""

    if not value1 or not value2:
        return None

    return SequenceMatcher(None, value1, value2).ratio()


def match_score(record1, record2):
    """
    Calculate a weighted similarity score between two business records.

    Weights:
        Business name    = 60%
        Business address = 30%
        Country          = 10%
    """

    name1 = get_value(
        record1,
        "business_name_normalized",
        "business_name"
    )
    name2 = get_value(
        record2,
        "business_name_normalized",
        "business_name"
    )

    address1 = get_value(
        record1,
        "business_address_normalized",
        "business_address"
    )
    address2 = get_value(
        record2,
        "business_address_normalized",
        "business_address"
    )

    country1 = get_value(
        record1,
        "country_normalized",
        "country"
    )
    country2 = get_value(
        record2,
        "country_normalized",
        "country"
    )

    name_score = similarity(name1, name2)
    address_score = similarity(address1, address2)
    country_score = similarity(country1, country2)

    scores = []
    weights = []

    if name_score is not None:
        scores.append(name_score)
        weights.append(0.60)

    if address_score is not None:
        scores.append(address_score)
        weights.append(0.30)

    if country_score is not None:
        scores.append(country_score)
        weights.append(0.10)

    if not scores:
        return 0.0

    total_weight = sum(weights)

    return sum(
        score * weight
        for score, weight in zip(scores, weights)
    ) / total_weight


def is_match(record1, record2, threshold=0.75):
    """
    Determine whether two records are a match.

    Returns True when the combined score reaches the threshold.
    """

    return match_score(record1, record2) >= threshold


if __name__ == "__main__":
    print("Matching module loaded successfully.")