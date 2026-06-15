from typing import List
from .base_scraper import BaseScraper, ScrapedProduct


class MarksScraper(BaseScraper):
    retailer_name = "M&S"
    country = "uk"
    currency = "GBP"

    def fetch_products(self) -> List[ScrapedProduct]:
        # PoC representative dataset.
        # Replace this method with live retailer/API integration in MVP.
        rows = [('Whole Milk 2L', 'Dairy', 1.8, None), ('Butter 250g', 'Dairy', 2.2, None), ('Cheddar Cheese 400g', 'Dairy', 3.75, None), ('Greek Yogurt 500g', 'Dairy', 1.6, None), ('White Bread 800g', 'Bakery', 1.15, None), ('Brown Bread 800g', 'Bakery', 1.25, None), ('Burger Buns 6 Pack', 'Bakery', 1.7, None), ('Croissant 4 Pack', 'Bakery', 2.8, None), ('Frozen Peas 900g', 'Frozen', 1.8, None), ('Margherita Pizza', 'Frozen', 3.5, None), ('Oven Chips 1kg', 'Frozen', 2.6, None), ('Eggs 12 Pack', 'Meat', 2.6, None), ('Chicken Breast 600g', 'Meat', 5.95, None), ('Vegetarian Sausages', 'Meat', 2.8, None), ('Digestive Biscuits', 'Snacks', 1.45, None), ('Ready Salted Crisps 6 Pack', 'Snacks', 1.95, None), ('Milk Chocolate 100g', 'Snacks', 1.6, None), ('Cola 2L', 'Drinks', 2.0, None), ('Orange Juice 1L', 'Drinks', 1.75, None), ('Still Water 6 Pack', 'Drinks', 2.75, None), ('Laundry Detergent 30 Wash', 'Household', 6.5, None), ('Toilet Roll 9 Pack', 'Household', 5.5, None), ('Hand Soap 500ml', 'Household', 1.6, None)]

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
        return "https://www.marksandspencer.com/MSFindItemsByKeyword?searchTerm=" + query
