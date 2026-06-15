from typing import List

from scraper.base_scraper import BaseScraper, ScrapedProduct


POC_IMAGE = {
    "milk": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300",
    "bread": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300",
    "eggs": "https://images.unsplash.com/photo-1518569656558-1f25e69d93d7?w=300",
    "butter": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=300",
    "cheese": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=300",
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=300",
    "default": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300",
}

POC_PRODUCTS = [
    ("Whole Milk 2L", "Dairy", "milk", 1.65, 120),
    ("Semi Skimmed Milk 2L", "Dairy", "milk", 1.60, 115),
    ("Greek Yogurt 500g", "Dairy", "milk", 1.25, 160),
    ("Natural Yogurt 500g", "Dairy", "milk", 1.15, 80),
    ("Butter 250g", "Dairy", "butter", 1.95, 145),
    ("Cheddar Cheese 400g", "Dairy", "cheese", 3.50, 280),
    ("Mozzarella Cheese 250g", "Dairy", "cheese", 2.25, 180),
    ("Paneer 200g", "Dairy", "cheese", 2.10, 95),
    ("Eggs 12 Pack", "Dairy", "eggs", 2.25, 95),

    ("White Bread 800g", "Bakery", "bread", 0.85, 65),
    ("Brown Bread 800g", "Bakery", "bread", 0.95, 75),
    ("Burger Buns 6 Pack", "Bakery", "bread", 1.20, 55),
    ("Pav 6 Pack", "Bakery", "bread", 1.10, 45),
    ("Croissant 4 Pack", "Bakery", "bread", 2.00, 160),
    ("Bagels 5 Pack", "Bakery", "bread", 1.80, 150),
    ("Garlic Bread", "Bakery", "bread", 1.40, 95),
    ("Naan Bread", "Bakery", "bread", 1.35, 80),
    ("Tortilla Wraps", "Bakery", "bread", 1.50, 130),

    ("Margherita Pizza", "Frozen", "pizza", 2.75, 190),
    ("Frozen Peas 900g", "Frozen", "default", 1.40, 155),
    ("Frozen Sweetcorn 750g", "Frozen", "default", 1.35, 140),
    ("Oven Chips 1kg", "Frozen", "default", 1.90, 220),
    ("Hash Browns", "Frozen", "default", 1.75, 180),
    ("Mixed Vegetables", "Frozen", "default", 1.50, 135),
    ("Ice Cream Tub", "Frozen", "default", 2.50, 220),

    ("Cola 2L", "Drinks", "default", 1.70, 100),
    ("Pepsi 2L", "Drinks", "default", 1.65, 95),
    ("Sprite 2L", "Drinks", "default", 1.60, 95),
    ("Orange Juice 1L", "Drinks", "default", 1.35, 120),
    ("Mango Juice 1L", "Drinks", "default", 1.45, 115),
    ("Still Water 6 Pack", "Drinks", "default", 2.20, 90),
    ("Red Bull 250ml", "Drinks", "default", 1.55, 125),
    ("Tea Bags 80 Pack", "Drinks", "default", 2.50, 190),
    ("Instant Coffee 200g", "Drinks", "default", 3.80, 320),

    ("Digestive Biscuits", "Snacks", "default", 1.25, 45),
    ("Oreo", "Snacks", "default", 1.20, 40),
    ("Bourbon Biscuits", "Snacks", "default", 1.10, 35),
    ("Milk Chocolate 100g", "Snacks", "default", 1.30, 90),
    ("Dairy Milk 36g", "Snacks", "default", 0.80, 45),
    ("KitKat 4 Pack", "Snacks", "default", 1.60, 80),
    ("Ready Salted Crisps 6 Pack", "Snacks", "default", 1.75, 120),
    ("Pringles", "Snacks", "default", 1.95, 110),

    ("Laundry Detergent 30 Wash", "Household", "default", 5.50, 310),
    ("Surf Excel Liquid 1L", "Household", "default", 4.95, 240),
    ("Dettol Handwash 750ml", "Household", "default", 2.75, 160),
    ("Hand Soap 500ml", "Household", "default", 1.50, 85),
    ("Toilet Roll 9 Pack", "Household", "default", 4.50, 220),
    ("Kitchen Towels", "Household", "default", 2.20, 150),
    ("Dishwasher Tablets", "Household", "default", 6.50, 390),
    ("Surface Cleaner", "Household", "default", 1.80, 120),
    ("Washing Up Liquid", "Household", "default", 1.35, 95),
    ("Air Freshener", "Household", "default", 2.00, 150),

    ("Chicken Breast 600g", "Protein", "default", 4.50, 260),
    ("Chicken Nuggets", "Protein", "default", 2.80, 210),
    ("Vegetarian Sausages", "Protein", "default", 2.50, 190),
    ("Veg Nuggets 400g", "Protein", "default", 2.60, 160),
    ("Plant Based Burger", "Protein", "default", 3.00, 240),
]

RETAILER_FACTOR = {
    "ASDA": 0.96,
    "Morrisons": 0.99,
    "Tesco": 1.00,
    "Sainsburys": 1.08,
    "M&S": 1.18,

    "DMart": 0.92,
    "JioMart": 0.96,
    "Blinkit": 1.08,
    "BigBasket": 1.00,
}

INDIA_RETAILERS = {"DMart", "JioMart", "Blinkit", "BigBasket"}
LOYALTY_RETAILERS = {
    "Tesco",
    "Sainsburys",
    "Morrisons",
    "M&S",
    "DMart",
    "JioMart",
    "BigBasket",
}


class MockRetailerScraper(BaseScraper):
    def __init__(self, retailer: str):
        self.retailer = retailer
        self.retailer_name = retailer

        self.is_india = retailer in INDIA_RETAILERS
        self.country = "india" if self.is_india else "uk"
        self.currency = "INR" if self.is_india else "GBP"

    def fetch_products(self) -> List[ScrapedProduct]:
        products: List[ScrapedProduct] = []
        factor = RETAILER_FACTOR.get(self.retailer, 1.0)

        for index, (name, category, key, uk_price, india_price) in enumerate(POC_PRODUCTS):
            base_price = india_price if self.is_india else uk_price
            price = round(base_price * factor, 2)

            loyalty_discount = 5 if self.is_india else 0.10
            loyalty_price = (
                round(max(price - loyalty_discount, 0.01), 2)
                if self.retailer in LOYALTY_RETAILERS
                else None
            )

            promotion = None
            if index in {0, 9, 10}:
                promotion = "Price matched"
            elif self.is_india and self.retailer in {"DMart", "JioMart"} and index % 7 == 0:
                promotion = "Member price"
            elif not self.is_india and self.retailer in {"Tesco", "Sainsburys"} and index % 8 == 0:
                promotion = "Club price"

            products.append(
                ScrapedProduct(
                    name=name,
                    retailer=self.retailer,
                    category=category,
                    price=price,
                    currency=self.currency,
                    country=self.country,
                    loyalty_price=loyalty_price,
                    promotion=promotion,
                    image_url=POC_IMAGE.get(key, POC_IMAGE["default"]),
                    product_url=f"https://www.{self.retailer.lower().replace('&', 'and').replace(' ', '')}.com/",
                )
            )

        return products