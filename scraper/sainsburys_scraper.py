from typing import List
from .base_scraper import BaseScraper, ScrapedProduct


class SainsburysScraper(BaseScraper):
    retailer_name = "Sainsburys"
    country = "uk"
    currency = "GBP"

    def fetch_products(self) -> List[ScrapedProduct]:
        # PoC representative dataset.
        # Replace this method with live retailer/API integration in MVP.
        rows = [('Whole Milk 2L', 'Dairy', 1.75, 1.65), ('Butter 250g', 'Dairy', 2.0, 1.9), ('Cheddar Cheese 400g', 'Dairy', 3.35, 3.1), ('Greek Yogurt 500g', 'Dairy', 1.35, None), ('White Bread 800g', 'Bakery', 0.95, None), ('Brown Bread 800g', 'Bakery', 1.05, None), ('Burger Buns 6 Pack', 'Bakery', 1.45, None), ('Croissant 4 Pack', 'Bakery', 2.4, None), ('Frozen Peas 900g', 'Frozen', 1.55, None), ('Margherita Pizza', 'Frozen', 2.95, 2.7), ('Oven Chips 1kg', 'Frozen', 2.2, None), ('Eggs 12 Pack', 'Meat', 2.4, None), ('Chicken Breast 600g', 'Meat', 5.25, None), ('Vegetarian Sausages', 'Meat', 2.35, None), ('Digestive Biscuits', 'Snacks', 1.2, None), ('Ready Salted Crisps 6 Pack', 'Snacks', 1.7, None), ('Milk Chocolate 100g', 'Snacks', 1.35, None), ('Cola 2L', 'Drinks', 1.8, 1.65), ('Orange Juice 1L', 'Drinks', 1.5, None), ('Still Water 6 Pack', 'Drinks', 2.3, None), ('Laundry Detergent 30 Wash', 'Household', 5.8, 5.5), ('Toilet Roll 9 Pack', 'Household', 4.95, None), ('Hand Soap 500ml', 'Household', 1.3, None)]

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
        return "https://www.sainsburys.co.uk/gol-ui/SearchResults/" + query
