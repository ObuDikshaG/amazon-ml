import re
import math
import unicodedata


def normalize_text(text):
    if text is None:
        return ""

    if isinstance(text, float) and math.isnan(text):
        return ""

    text = str(text)

    # Normalize Unicode compatibility forms
    text = unicodedata.normalize("NFKC", text)

    # Lowercase where applicable
    text = text.lower()

    # Preserve Unicode letters, numbers, and combining marks.
    # Replace punctuation/symbols with spaces.
    cleaned = []

    for char in text:
        category = unicodedata.category(char)

        if category[0] in ("L", "N") or category.startswith("M"):
            cleaned.append(char)
        else:
            cleaned.append(" ")

    text = "".join(cleaned)

    # Collapse repeated whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


if __name__ == "__main__":
    examples = [
        "ABC Pvt. Ltd.",
        "Christ Chapel",
        "H.No.16-11-23/37/A, 2Nd Floor",
        "Callicoat & Dailey Inc",
        "राम मार्केटिंग प्राइवेट लिमिटेड",
        "आदित्य प्रॉपर्टीज एलएलपी",
    ]

    for example in examples:
        print(example, " -> ", normalize_text(example))