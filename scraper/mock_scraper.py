from typing import List

from scraper.base_scraper import BaseScraper, ScrapedProduct


POC_IMAGE = {
    "milk": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300",
    "yogurt": "https://images.unsplash.com/photo-1571212515416-fef01fc43637?w=300",
    "bread": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300",
    "buns": "https://images.unsplash.com/photo-1573246123716-6b1782bfc499?w=300",
    "croissant": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=300",
    "eggs": "https://images.unsplash.com/photo-1518569656558-1f25e69d93d7?w=300",
    "butter": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=300",
    "cheese": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=300",
    "paneer": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=300",
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=300",
    "peas": "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=300",
    "sweetcorn": "https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=300",
    "chips": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=300",
    "hashbrowns": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=300",
    "mixedveg": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=300",
    "icecream": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=300",
    "cola": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=300",
    "juice": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=300",
    "water": "https://images.unsplash.com/photo-1616118132534-381148898bb4?w=300",
    "energy": "https://images.unsplash.com/photo-1622543925917-763c34d1a86e?w=300",
    "tea": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=300",
    "coffee": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=300",
    "biscuit": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=300",
    "chocolate": "https://images.unsplash.com/photo-1511381939415-e44015466834?w=300",
    "crisps": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=300",
    "detergent": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=300",
    "soap": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=300",
    "toiletroll": "https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=300",
    "cleaner": "https://images.unsplash.com/photo-1585421514284-efb74c2b69ba?w=300",
    "airfreshener": "https://images.unsplash.com/photo-1528756514091-dee5ecaa3278?w=300",
    "chicken": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=300",
    "vegprotein": "https://images.unsplash.com/photo-1585238342024-78d387f4a707?w=300",
    "default": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300",
}

# name, category, image-key, uk base price, india base price
POC_PRODUCTS = [
    ("Whole Milk 2L", "Dairy", "milk", 1.65, 120),
    ("Semi Skimmed Milk 2L", "Dairy", "milk", 1.60, 115),
    ("Greek Yogurt 500g", "Dairy", "yogurt", 1.25, 160),
    ("Natural Yogurt 500g", "Dairy", "yogurt", 1.15, 80),
    ("Butter 250g", "Dairy", "butter", 1.95, 145),
    ("Cheddar Cheese 400g", "Dairy", "cheese", 3.50, 280),
    ("Mozzarella Cheese 250g", "Dairy", "cheese", 2.25, 180),
    ("Paneer 200g", "Dairy", "paneer", 2.10, 95),
    ("Eggs 12 Pack", "Dairy", "eggs", 2.25, 95),

    ("White Bread 800g", "Bakery", "bread", 0.85, 65),
    ("Brown Bread 800g", "Bakery", "bread", 0.95, 75),
    ("Burger Buns 6 Pack", "Bakery", "buns", 1.20, 55),
    ("Pav 6 Pack", "Bakery", "buns", 1.10, 45),
    ("Croissant 4 Pack", "Bakery", "croissant", 2.00, 160),
    ("Bagels 5 Pack", "Bakery", "bread", 1.80, 150),
    ("Garlic Bread", "Bakery", "bread", 1.40, 95),
    ("Naan Bread", "Bakery", "bread", 1.35, 80),
    ("Tortilla Wraps", "Bakery", "bread", 1.50, 130),

    ("Margherita Pizza", "Frozen", "pizza", 2.75, 190),
    ("Frozen Peas 900g", "Frozen", "peas", 1.40, 155),
    ("Frozen Sweetcorn 750g", "Frozen", "sweetcorn", 1.35, 140),
    ("Oven Chips 1kg", "Frozen", "chips", 1.90, 220),
    ("Hash Browns", "Frozen", "hashbrowns", 1.75, 180),
    ("Mixed Vegetables", "Frozen", "mixedveg", 1.50, 135),
    ("Ice Cream Tub", "Frozen", "icecream", 2.50, 220),

    ("Cola 2L", "Drinks", "cola", 1.70, 100),
    ("Pepsi 2L", "Drinks", "cola", 1.65, 95),
    ("Sprite 2L", "Drinks", "cola", 1.60, 95),
    ("Orange Juice 1L", "Drinks", "juice", 1.35, 120),
    ("Mango Juice 1L", "Drinks", "juice", 1.45, 115),
    ("Still Water 6 Pack", "Drinks", "water", 2.20, 90),
    ("Red Bull 250ml", "Drinks", "energy", 1.55, 125),
    ("Tea Bags 80 Pack", "Drinks", "tea", 2.50, 190),
    ("Instant Coffee 200g", "Drinks", "coffee", 3.80, 320),

    ("Digestive Biscuits", "Snacks", "biscuit", 1.25, 45),
    ("Oreo", "Snacks", "biscuit", 1.20, 40),
    ("Bourbon Biscuits", "Snacks", "biscuit", 1.10, 35),
    ("Milk Chocolate 100g", "Snacks", "chocolate", 1.30, 90),
    ("Dairy Milk 36g", "Snacks", "chocolate", 0.80, 45),
    ("KitKat 4 Pack", "Snacks", "chocolate", 1.60, 80),
    ("Ready Salted Crisps 6 Pack", "Snacks", "crisps", 1.75, 120),
    ("Pringles", "Snacks", "crisps", 1.95, 110),

    ("Laundry Detergent 30 Wash", "Household", "detergent", 5.50, 310),
    ("Surf Excel Liquid 1L", "Household", "detergent", 4.95, 240),
    ("Dettol Handwash 750ml", "Household", "soap", 2.75, 160),
    ("Hand Soap 500ml", "Household", "soap", 1.50, 85),
    ("Toilet Roll 9 Pack", "Household", "toiletroll", 4.50, 220),
    ("Kitchen Towels", "Household", "toiletroll", 2.20, 150),
    ("Dishwasher Tablets", "Household", "cleaner", 6.50, 390),
    ("Surface Cleaner", "Household", "cleaner", 1.80, 120),
    ("Washing Up Liquid", "Household", "soap", 1.35, 95),
    ("Air Freshener", "Household", "airfreshener", 2.00, 150),

    ("Chicken Breast 600g", "Protein", "chicken", 4.50, 260),
    ("Chicken Nuggets", "Protein", "chicken", 2.80, 210),
    ("Vegetarian Sausages", "Protein", "vegprotein", 2.50, 190),
    ("Veg Nuggets 400g", "Protein", "vegprotein", 2.60, 160),
    ("Plant Based Burger", "Protein", "vegprotein", 3.00, 240),
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

RETAILER_URLS = {
    "Tesco": "https://www.tesco.com/groceries/",
    "ASDA": "https://groceries.asda.com/",
    "Morrisons": "https://groceries.morrisons.com/",
    "Sainsburys": "https://www.sainsburys.co.uk/gol-ui/groceries",
    "M&S": "https://www.marksandspencer.com/c/food-to-order",
    "DMart": "https://www.dmart.in/",
    "JioMart": "https://www.jiomart.com/",
    "Blinkit": "https://blinkit.com/",
    "BigBasket": "https://www.bigbasket.com/",
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
                    product_url=RETAILER_URLS.get(self.retailer),
                )
            )

        return products
