from collections import Counter

HIGH_CONFIDENCE_KEYWORDS = {"water main break", "flood", "burst pipe", "road closed", "crews on scene"}
MEDIUM_CONFIDENCE_KEYWORDS = {"water leak", "no water", "water outage", "sinkhole", "low pressure"}


def compute_confidence(signals_text: list[str], source_types: list[str]) -> tuple[float, dict]:
    normalized = " ".join(signals_text).lower()

    high_hits = sum(1 for keyword in HIGH_CONFIDENCE_KEYWORDS if keyword in normalized)
    medium_hits = sum(1 for keyword in MEDIUM_CONFIDENCE_KEYWORDS if keyword in normalized)
    unique_sources = len(set(source_types))

    score = min(100.0, (high_hits * 25.0) + (medium_hits * 10.0) + (unique_sources * 15.0))
    breakdown = {
        "high_keyword_hits": high_hits,
        "medium_keyword_hits": medium_hits,
        "source_diversity": unique_sources,
        "source_distribution": dict(Counter(source_types)),
        "formula": "min(100, high*25 + medium*10 + unique_sources*15)",
    }
    return score, breakdown
