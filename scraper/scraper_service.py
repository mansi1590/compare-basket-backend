from typing import List, Dict

from .tesco_scraper import TescoScraper
from .asda_scraper import AsdaScraper
from .morrisons_scraper import MorrisonsScraper
from .sainsburys_scraper import SainsburysScraper
from .marks_scraper import MarksScraper
from .india_scraper import IndiaScraper


class ScraperService:
    """Runs all retailer adapters and returns normalized rows.

    PoC behavior:
    - Uses representative retailer datasets.
    - Validates architecture, data normalization, product matching, price history and basket comparison.
    MVP behavior:
    - Replace adapter fetch_products() with live integrations / scheduled scraping.
    """

    def __init__(self):
        self.adapters = [
            TescoScraper(),
            AsdaScraper(),
            MorrisonsScraper(),
            SainsburysScraper(),
            MarksScraper(),
            IndiaScraper(),
        ]

    def run_all(self) -> List[Dict]:
        rows: List[Dict] = []
        for adapter in self.adapters:
            rows.extend(adapter.run())
        return rows


if __name__ == "__main__":
    products = ScraperService().run_all()
    print(f"Fetched {len(products)} normalized products")
    for product in products[:5]:
        print(product)
