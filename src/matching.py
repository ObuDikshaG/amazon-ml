import pandas as pd
from difflib import SequenceMatcher


def normalize_text(value):
    """Normalize text for comparison."""
    if pd.isna(value):
        return ""
    return str(value).lower().strip()


def similarity(a, b):
    """Return similarity between two text values."""
    a = normalize_text(a)
    b = normalize_text(b)

    # Both values missing
    if not a and not b:
        return None

    # One value missing
    if not a or not b:
        return None

    return SequenceMatcher(None, a, b).ratio()


def match_score(record1, record2):
    """
    Calculate a matching score between two business records.

    The score uses only fields that are available in both records.
    """

    scores = []
    weights = []

    name_score = similarity(
        record1["business_name"],
        record2["business_name"]
    )

    if name_score is not None:
        scores.append(name_score)
        weights.append(0.6)

    address_score = similarity(
        record1["business_address"],
        record2["business_address"]
    )

    if address_score is not None:
        scores.append(address_score)
        weights.append(0.3)

    country_score = similarity(
        record1["country"],
        record2["country"]
    )

    if country_score is not None:
        scores.append(country_score)
        weights.append(0.1)

    if not scores:
        return 0.0

    # Re-normalize weights when some fields are missing
    total_weight = sum(weights)
    score = sum(
        score * weight
        for score, weight in zip(scores, weights)
    ) / total_weight

    return score


def is_match(record1, record2, threshold=0.75):
    """Return True if two records are considered a match."""
    return match_score(record1, record2) >= threshold


if __name__ == "__main__":
    print("Matching module loaded successfully.")
    