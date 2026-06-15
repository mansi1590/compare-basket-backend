from typing import List
from .base_scraper import BaseScraper, ScrapedProduct


class IndiaScraper(BaseScraper):
    country = "india"
    currency = "INR"

    def fetch_products(self) -> List[ScrapedProduct]:
        rows = [
            ("Amul Milk 1L", "Dairy", {"DMart": 66, "JioMart": 67, "Blinkit": 70, "BigBasket": 68}),
            ("Amul Butter 500g", "Dairy", {"DMart": 275, "JioMart": 280, "Blinkit": 290, "BigBasket": 285}),
            ("Britannia Cheese Slices", "Dairy", {"DMart": 128, "JioMart": 132, "Blinkit": 140, "BigBasket": 135}),
            ("Britannia Bread 400g", "Bakery", {"DMart": 45, "JioMart": 48, "Blinkit": 50, "BigBasket": 49}),
            ("Pav 6 Pack", "Bakery", {"DMart": 36, "JioMart": 38, "Blinkit": 42, "BigBasket": 40}),
            ("Frozen Green Peas 500g", "Frozen", {"DMart": 95, "JioMart": 98, "Blinkit": 110, "BigBasket": 105}),
            ("Frozen French Fries 750g", "Frozen", {"DMart": 165, "JioMart": 170, "Blinkit": 185, "BigBasket": 178}),
            ("Eggs 12 Pack", "Meat", {"DMart": 95, "JioMart": 98, "Blinkit": 105, "BigBasket": 99}),
            ("Veg Nuggets 400g", "Meat", {"DMart": 145, "JioMart": 150, "Blinkit": 165, "BigBasket": 158}),
            ("Parle-G Biscuits 800g", "Snacks", {"DMart": 82, "JioMart": 85, "Blinkit": 90, "BigBasket": 88}),
            ("Lays Chips 52g", "Snacks", {"DMart": 20, "JioMart": 20, "Blinkit": 22, "BigBasket": 22}),
            ("Dairy Milk 36g", "Snacks", {"DMart": 38, "JioMart": 40, "Blinkit": 45, "BigBasket": 42}),
            ("Coca Cola 2L", "Drinks", {"DMart": 92, "JioMart": 95, "Blinkit": 105, "BigBasket": 100}),
            ("Real Orange Juice 1L", "Drinks", {"DMart": 105, "JioMart": 110, "Blinkit": 120, "BigBasket": 115}),
            ("Bisleri Water 1L", "Drinks", {"DMart": 18, "JioMart": 20, "Blinkit": 22, "BigBasket": 20}),
            ("Surf Excel Liquid 1L", "Household", {"DMart": 210, "JioMart": 218, "Blinkit": 230, "BigBasket": 225}),
            ("Toilet Roll 6 Pack", "Household", {"DMart": 170, "JioMart": 175, "Blinkit": 190, "BigBasket": 185}),
            ("Dettol Handwash 750ml", "Household", {"DMart": 115, "JioMart": 120, "Blinkit": 130, "BigBasket": 125}),
        ]

        products: List[ScrapedProduct] = []
        for name, category, retailer_prices in rows:
            for retailer, price in retailer_prices.items():
                products.append(
                    ScrapedProduct(
                        name=name,
                        retailer=retailer,
                        category=category,
                        price=float(price),
                        currency=self.currency,
                        country=self.country,
                        product_url=self.product_url_for(retailer, name),
                    )
                )

        return products

    def product_url_for(self, retailer: str, name: str) -> str:
        query = name.replace(" ", "%20")
        urls = {
            "DMart": "https://www.dmart.in/search?searchTerm=",
            "JioMart": "https://www.jiomart.com/search/",
            "Blinkit": "https://blinkit.com/s/?q=",
            "BigBasket": "https://www.bigbasket.com/ps/?q=",
        }
        return urls.get(retailer, "https://www.google.com/search?q=") + query
