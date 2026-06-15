from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class ScrapedProduct:
    name: str
    retailer: str
    category: str
    price: float
    currency: str
    country: str
    loyalty_price: Optional[float] = None
    unit_price: Optional[float] = None
    promotion: Optional[str] = None
    product_url: Optional[str] = None
    image_url: Optional[str] = None
    observed_at: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["observed_at"] = data["observed_at"] or datetime.now(timezone.utc).isoformat()
        return data


class BaseScraper(ABC):
    retailer_name: str = ""
    country: str = "uk"
    currency: str = "GBP"

    @abstractmethod
    def fetch_products(self) -> List[ScrapedProduct]:
        """Return normalized products for one retailer."""
        raise NotImplementedError

    def run(self) -> List[dict]:
        """Entrypoint used by scraper service."""
        return [product.to_dict() for product in self.fetch_products()]
