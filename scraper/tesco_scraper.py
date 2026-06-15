from typing import List
from .base_scraper import BaseScraper, ScrapedProduct


class TescoScraper(BaseScraper):
    retailer_name = "Tesco"
    country = "uk"
    currency = "GBP"

    def fetch_products(self) -> List[ScrapedProduct]:
        # PoC representative dataset.
        # Replace this method with live retailer/API integration in MVP.
        rows = [('Whole Milk 2L', 'Dairy', 1.65, 1.55), ('Butter 250g', 'Dairy', 1.85, None), ('Cheddar Cheese 400g', 'Dairy', 3.1, 2.9), ('Greek Yogurt 500g', 'Dairy', 1.25, None), ('White Bread 800g', 'Bakery', 0.85, 0.8), ('Brown Bread 800g', 'Bakery', 0.95, None), ('Burger Buns 6 Pack', 'Bakery', 1.3, None), ('Croissant 4 Pack', 'Bakery', 2.2, None), ('Frozen Peas 900g', 'Frozen', 1.4, None), ('Margherita Pizza', 'Frozen', 2.75, 2.5), ('Oven Chips 1kg', 'Frozen', 2.0, None), ('Eggs 12 Pack', 'Meat', 2.25, None), ('Chicken Breast 600g', 'Meat', 4.95, 4.75), ('Vegetarian Sausages', 'Meat', 2.2, None), ('Digestive Biscuits', 'Snacks', 1.1, None), ('Ready Salted Crisps 6 Pack', 'Snacks', 1.55, None), ('Milk Chocolate 100g', 'Snacks', 1.25, None), ('Cola 2L', 'Drinks', 1.7, 1.55), ('Orange Juice 1L', 'Drinks', 1.35, None), ('Still Water 6 Pack', 'Drinks', 2.1, None), ('Laundry Detergent 30 Wash', 'Household', 5.5, 5.0), ('Toilet Roll 9 Pack', 'Household', 4.75, None), ('Hand Soap 500ml', 'Household', 1.2, None)]

        return [
            ScrapedProduct(
                name=name,
                retailer=self.retailer_name,
                category=category,
                price=price,
                loyalty_price=loyalty_price,
                currency=self.currency,
                country=self.country,
                product_url=self.product_url_for(name),
            )
            for name, category, price, loyalty_price in rows
        ]

    def product_url_for(self, name: str) -> str:
        query = name.replace(" ", "+")
        return "https://www.tesco.com/groceries/en-GB/search?query=" + query
