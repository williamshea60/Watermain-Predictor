from datetime import datetime, timezone

from app.jobs.rss_utils import build_source_id, entry_datetime, is_duplicate, parse_feed


def test_parse_sample_rss_xml_string() -> None:
    rss_xml = """<?xml version="1.0"?>
    <rss version="2.0"><channel><title>Test Feed</title>
      <item>
        <title>Water main break at King &amp; Bathurst</title>
        <description>Crew dispatched</description>
        <link>https://example.com/1</link>
        <guid>abc-123</guid>
        <pubDate>Tue, 10 Sep 2024 14:30:00 GMT</pubDate>
      </item>
    </channel></rss>
    """

    parsed = parse_feed(rss_xml)

    assert len(parsed.entries) == 1
    entry = parsed.entries[0]
    assert entry.title == "Water main break at King & Bathurst"
    assert entry.summary == "Crew dispatched"
    assert entry.link == "https://example.com/1"
    assert build_source_id(entry, entry.link) == "abc-123"

    observed = entry_datetime(entry, datetime.now(timezone.utc))
    assert observed.year == 2024
    assert observed.tzinfo is not None


def test_source_id_hashes_link_when_feed_entry_has_no_id_or_guid() -> None:
    rss_xml = """<?xml version="1.0"?>
    <rss version="2.0"><channel><title>Test Feed</title>
      <item>
        <title>Water disruption update</title>
        <description>Repair in progress</description>
        <link>https://example.com/no-guid</link>
      </item>
    </channel></rss>
    """

    parsed = parse_feed(rss_xml)
    entry = parsed.entries[0]

    source_id = build_source_id(entry, entry.link)

    assert source_id
    assert source_id != entry.link


def test_dedupe_prefers_url_or_source_pair() -> None:
    assert is_duplicate(url_match=True, source_match=False) is True
    assert is_duplicate(url_match=False, source_match=True) is True
    assert is_duplicate(url_match=False, source_match=False) is False
