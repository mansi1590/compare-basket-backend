from typing import List
from .base_scraper import BaseScraper, ScrapedProduct


class MorrisonsScraper(BaseScraper):
    retailer_name = "Morrisons"
    country = "uk"
    currency = "GBP"

    def fetch_products(self) -> List[ScrapedProduct]:
        # PoC representative dataset.
        # Replace this method with live retailer/API integration in MVP.
        rows = [('Whole Milk 2L', 'Dairy', 1.6, None), ('Butter 250g', 'Dairy', 1.85, None), ('Cheddar Cheese 400g', 'Dairy', 3.2, None), ('Greek Yogurt 500g', 'Dairy', 1.3, None), ('White Bread 800g', 'Bakery', 0.88, None), ('Brown Bread 800g', 'Bakery', 0.98, None), ('Burger Buns 6 Pack', 'Bakery', 1.35, None), ('Croissant 4 Pack', 'Bakery', 2.25, None), ('Frozen Peas 900g', 'Frozen', 1.45, None), ('Margherita Pizza', 'Frozen', 2.7, None), ('Oven Chips 1kg', 'Frozen', 2.05, None), ('Eggs 12 Pack', 'Meat', 2.2, None), ('Chicken Breast 600g', 'Meat', 5.0, None), ('Vegetarian Sausages', 'Meat', 2.15, None), ('Digestive Biscuits', 'Snacks', 1.12, None), ('Ready Salted Crisps 6 Pack', 'Snacks', 1.58, None), ('Milk Chocolate 100g', 'Snacks', 1.2, None), ('Cola 2L', 'Drinks', 1.65, None), ('Orange Juice 1L', 'Drinks', 1.4, None), ('Still Water 6 Pack', 'Drinks', 2.15, None), ('Laundry Detergent 30 Wash', 'Household', 5.45, None), ('Toilet Roll 9 Pack', 'Household', 4.65, None), ('Hand Soap 500ml', 'Household', 1.15, None)]

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
        return "https://groceries.morrisons.com/search?entry=" + query
