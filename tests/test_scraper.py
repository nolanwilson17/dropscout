from pathlib import Path
from dropscout.scraper import parse_html
from dropscout.scraper import parse_url, _cache_path


def test_parse_html_core_fields():
    sample = Path(__file__).parent / "amazon_sample.html"
    info = parse_html(sample)

    # Minimal sanity checks — expand later
    assert info.title is not None
    assert info.price is not None
    assert info.seller is not None


AMAZON = "https://www.amazon.com/Changing-Control-Lighting-Flexible-Decoration/dp/B09V366BDY?crid=5L4XSIIXJXFM&dib=eyJ2IjoiMSJ9.fnuMC83zm3YtykKkFrUEfc07rlyswtUAwDSmddKSqM0peEGgNFrYiQR_i-WQKApBaPqFSQJfwRxsKUZvIBf4IEjeaO2sP7nZk8_uKTYWtlHeGhhgc0CuR6s5UQkEcvcqAlN57uy-6JF74XkPhiNU0Q4qEYSURYrY3hWmnmEHwVMn0abhhTZg-TsPcoTemab0TKgduhIR3rlqeCkpFH_avXiW-524KzspzUUz-yD7iam9SU3lKIpYIiny9aZauWr6_POmP1hsUX99WYcCsFV83PCf2djipl1ypWJ7EKb_XB8.D0y_BcQRc173YXzEW7dWkyCvAlDdf7QltjXc3Vlej9I&dib_tag=se&keywords=led%2Blights&qid=1750712833&sprefix=led%2Bligths%2Caps%2C92&sr=8-8&th=1"


def test_parse_url_caches_and_parses():
    # first call – downloads + caches
    info = parse_url(AMAZON, force_refresh=True)
    assert info.title is not None
    assert info.price is not None
    assert _cache_path(AMAZON).exists()

    # second call – should hit only the cache (fast, no network)
    info2 = parse_url(AMAZON)
    assert info2.title == info.title
    assert info2.price == info.price
