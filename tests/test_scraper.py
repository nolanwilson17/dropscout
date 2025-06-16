from pathlib import Path
from dropscout.scraper import parse_html          # or whatever your function is named

def test_parse_html_core_fields():
    sample = Path(__file__).parent / "amazon_sample.html"
    info = parse_html(sample)

    # Minimal sanity checks — expand later
    assert info.title is not None
    assert info.price is not None
    assert info.seller is not None