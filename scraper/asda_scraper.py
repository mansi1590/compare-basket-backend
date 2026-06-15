from typing import List
from .base_scraper import BaseScraper, ScrapedProduct


class AsdaScraper(BaseScraper):
    retailer_name = "ASDA"
    country = "uk"
    currency = "GBP"

    def fetch_products(self) -> List[ScrapedProduct]:
        # PoC representative dataset.
        # Replace this method with live retailer/API integration in MVP.
        rows = [('Whole Milk 2L', 'Dairy', 1.6, None), ('Butter 250g', 'Dairy', 1.9, None), ('Cheddar Cheese 400g', 'Dairy', 3.0, None), ('Greek Yogurt 500g', 'Dairy', 1.2, None), ('White Bread 800g', 'Bakery', 0.8, None), ('Brown Bread 800g', 'Bakery', 0.9, None), ('Burger Buns 6 Pack', 'Bakery', 1.2, None), ('Croissant 4 Pack', 'Bakery', 2.1, None), ('Frozen Peas 900g', 'Frozen', 1.35, None), ('Margherita Pizza', 'Frozen', 2.6, None), ('Oven Chips 1kg', 'Frozen', 1.95, None), ('Eggs 12 Pack', 'Meat', 2.2, None), ('Chicken Breast 600g', 'Meat', 4.85, None), ('Vegetarian Sausages', 'Meat', 2.1, None), ('Digestive Biscuits', 'Snacks', 1.0, None), ('Ready Salted Crisps 6 Pack', 'Snacks', 1.5, None), ('Milk Chocolate 100g', 'Snacks', 1.15, None), ('Cola 2L', 'Drinks', 1.6, None), ('Orange Juice 1L', 'Drinks', 1.3, None), ('Still Water 6 Pack', 'Drinks', 2.0, None), ('Laundry Detergent 30 Wash', 'Household', 5.25, None), ('Toilet Roll 9 Pack', 'Household', 4.5, None), ('Hand Soap 500ml', 'Household', 1.1, None)]

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
        return "https://groceries.asda.com/search/" + query
