from backend_worker.geocoding import GeocodeResult
from backend_worker.rss_ingestion import extract_toronto_location_text, ingest_from_feed_content


class FakeGeocoder:
    def geocode(self, location_text: str):
        return GeocodeResult(latitude=43.6532, longitude=-79.3832, provider="fake", confidence=0.9)


SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>City Alerts</title>
    <item>
      <title>Watermain break near Queen &amp; Bathurst</title>
      <description>Crews responding near 200 Queen Street West in Toronto.</description>
      <link>https://example.com/alerts/1</link>
      <pubDate>Tue, 04 Jun 2024 14:30:00 GMT</pubDate>
    </item>
    <item>
      <title>General infrastructure update</title>
      <description>No service impact in the Annex today.</description>
      <link>https://example.com/alerts/2</link>
      <pubDate>Tue, 04 Jun 2024 16:30:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


def test_ingest_parses_items_and_required_fields():
    signals = ingest_from_feed_content(
        SAMPLE_FEED,
        source_feed_url="https://example.com/rss",
        geocoder=FakeGeocoder(),
    )

    assert len(signals) == 2
    first = signals[0]
    assert first.title == "Watermain break near Queen & Bathurst"
    assert first.summary.startswith("Crews responding")
    assert first.item_url == "https://example.com/alerts/1"
    assert first.published_at is not None
    assert first.location_text == "Queen & Bathurst"
    assert first.geocode is not None


def test_ingest_applies_keyword_filters():
    signals = ingest_from_feed_content(
        SAMPLE_FEED,
        source_feed_url="https://example.com/rss",
        keyword_filters=["watermain", "burst"],
    )

    assert len(signals) == 1
    assert signals[0].item_url == "https://example.com/alerts/1"
    assert signals[0].matched_keywords == ["watermain"]


def test_extract_location_text_heuristics():
    assert extract_toronto_location_text("Issue at King & Spadina intersection") == "King & Spadina"
    assert extract_toronto_location_text("Repair at 1200 Danforth Avenue tonight") == "1200 Danforth Avenue"
    assert extract_toronto_location_text("Residents in liberty village should expect delays") == "Liberty Village"
    assert extract_toronto_location_text("No Toronto location provided") is None
