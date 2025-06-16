from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ProductInfo:
    url: str
    title: Optional[str]
    price: Optional[float]      # numeric—no $ sign
    currency: Optional[str]     # "USD", "GBP", …
    seller: Optional[str]
    ships_from: Optional[str]
    delivery_estimate: Optional[str]
    description: Optional[str]
    image_urls: List[str]       # first 1–4 image links