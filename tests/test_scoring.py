from app.services.scoring import compute_confidence


def test_confidence_reflects_keyword_hits_and_source_diversity() -> None:
    score, breakdown = compute_confidence(
        signals_text=[
            "Water main break reported and road closed",
            "Crews on scene for burst pipe",
            "Water outage in area",
        ],
        source_types=["rss", "reddit", "rss"],
    )

    assert score > 0
    assert breakdown["high_keyword_hits"] >= 1
    assert breakdown["source_diversity"] == 2
    assert "formula" in breakdown


def test_confidence_is_capped_at_100() -> None:
    score, _ = compute_confidence(
        signals_text=["water main break flood burst pipe road closed crews on scene"] * 10,
        source_types=["rss", "reddit", "x", "y", "z"],
    )

    assert score == 100.0
