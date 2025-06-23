from pathlib import Path
from datetime import datetime, timezone
import hashlib
import re
from typing import Optional, Tuple

import requests   # make sure “requests” is in requirements.txt
from bs4 import BeautifulSoup

from .models import ProductInfo

# ─── cache folder (one per repo clone) ─────────────────────────────────────────
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(url: str) -> Path:
    """
    Deterministic local filename for a given product URL.
    Example:  md5("https://amazon.com/abc")[:12]  →  data/raw/3fa4b0c9caad.html
    """
    slug = hashlib.md5(url.encode()).hexdigest()[:12]
    return CACHE_DIR / f"{slug}.html"


# ---------------------------------------------------------------------------
# Helper: robust price-and-currency extraction
# ---------------------------------------------------------------------------
_CURRENCY_MAP = {"$": "USD", "£": "GBP", "€": "EUR"}


def _parse_price(price_el) -> Tuple[Optional[float], Optional[str]]:
    """
    Return (numeric_price, currency) from a BeautifulSoup element,
    or (None, None) if the element is missing / empty / unparsable.
    """
    if not price_el:
        return None, None

    raw = price_el.get_text(strip=True)
    if not raw:
        return None, None

    # Match things like "€1,234.56", "$199", "1 299,00 €", etc.
    m = re.search(r"([€£$])?\s*([\d.,\s]+)", raw)
    if not m:
        return None, None

    symbol, num = m.groups()
    try:
        value = float(num.replace(",", "").replace(
            " ", "").replace("\u202f", ""))
    except ValueError:
        return None, None

    currency = _CURRENCY_MAP.get(symbol, "USD")  # default to USD if unknown
    return value, currency


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------

def parse_html(html_path: Path) -> ProductInfo:
    raw = Path(html_path).read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(raw, "lxml")

    # -- TITLE --------------------------------------------------------------
    title = soup.select_one("#productTitle")

    # -- PRICE --------------------------------------------------------------
    price_el = (
        soup.select_one(".a-price .a-offscreen")
        or soup.select_one(".priceToPay .a-offscreen")
        or soup.select_one("#priceblock_ourprice")
    )
    numeric_price, currency = _parse_price(price_el)

    # -- SELLER -------------------------------------------------------------
    seller = soup.select_one(
        "#sellerProfileTriggerId") or soup.select_one("#tabular-buybox a")

    # -- SHIPS FROM ---------------------------------------------------------
    ships_label = soup.select_one(
        "#tabular-buybox span:-soup-contains('Ships from')")
    ships_from = ships_label.find_next("span").get_text(
        strip=True) if ships_label else None

    # -- IMAGES -------------------------------------------------------------
    image_urls = [
        img.get("src") or img.get("data-src") or img.get("data-old-hires")
        for img in soup.select("#main-image-container img")
        if img.get("src") or img.get("data-src") or img.get("data-old-hires")
    ][:4]

    # ----------------------------------------------------------------------
    return ProductInfo(
        url=str(html_path),
        title=title.get_text(strip=True) if title else None,
        price=numeric_price,
        currency=currency,
        seller=seller.get_text(strip=True) if seller else None,
        ships_from=ships_from,
        delivery_estimate=None,
        description=None,
        image_urls=image_urls,
    )


def parse_url(url: str, *, force_refresh: bool = False) -> ProductInfo:
    """
    Download a product page (unless it's already cached), save raw HTML, then
    reuse parse_html() to return a fully populated ProductInfo object.
    """
    cache_file = _cache_path(url)

    # use cached file unless caller forces a refresh
    if cache_file.exists() and not force_refresh:
        raw_path = cache_file
    else:
        headers = {
            "User-Agent": "dropscout-bot/0.1 (+https://github.com/nolanwilson17/dropscout)"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        cache_file.write_text(resp.text, encoding="utf-8")
        raw_path = cache_file
        action = "refreshed" if force_refresh else "cached"
        print(f"[{datetime.now(timezone.utc):%H:%M:%S}] {action} → {cache_file.name}")

    return parse_html(raw_path)
