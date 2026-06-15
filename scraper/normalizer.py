def canonical_name(name: str) -> str:
    value = name.lower().replace("semi-skimmed", "semi skimmed")
    replacements = {
        "2 litre": "2l",
        "2 liters": "2l",
        "800 grams": "800g",
        "12 eggs": "eggs 12 pack",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return " ".join(value.title().split())


def match_confidence(raw_name: str, canonical: str) -> float:
    raw_words = set(raw_name.lower().split())
    canonical_words = set(canonical.lower().split())
    if not raw_words or not canonical_words:
        return 0.0
    return round(len(raw_words & canonical_words) / len(raw_words | canonical_words), 2)
