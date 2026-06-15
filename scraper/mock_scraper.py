from scraper.base_scraper import BaseScraper, ScrapedItem

POC_IMAGE = {
    "milk": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300",
    "bread": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300",
    "eggs": "https://images.unsplash.com/photo-1518569656558-1f25e69d93d7?w=300",
    "butter": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=300",
    "cheese": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=300",
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=300",
}

POC_PRODUCTS = [
    ("Whole Milk 2L", "Dairy", "milk"),
    ("White Bread 800g", "Bakery", "bread"),
    ("Eggs 12 Pack", "Dairy", "eggs"),
    ("Butter 250g", "Dairy", "butter"),
    ("Cheddar Cheese 400g", "Dairy", "cheese"),
    ("Margherita Pizza", "Frozen", "pizza"),
]

PRICE_MATRIX = {
    "Tesco": [1.65, 0.85, 2.25, 1.95, 3.50, 2.75],
    "ASDA": [1.60, 0.80, 2.20, 1.85, 3.30, 2.50],
    "Morrisons": [1.60, 0.90, 2.20, 1.85, 3.60, 2.80],
    "Sainsburys": [1.75, 0.95, 2.40, 2.10, 3.75, 2.95],
    "M&S": [1.80, 1.00, 2.60, 2.20, 4.00, 3.25],
}

LOYALTY = {
    "Tesco": "Clubcard",
    "ASDA": "Rewards",
    "Morrisons": "More",
    "Sainsburys": "Nectar",
    "M&S": "Sparks",
}


class MockRetailerScraper(BaseScraper):
    def __init__(self, retailer: str):
        self.retailer = retailer

    def scrape(self):
        prices = PRICE_MATRIX[self.retailer]
        for index, (name, category, key) in enumerate(POC_PRODUCTS):
            price = prices[index]
            loyalty_price = round(price - 0.10, 2) if self.retailer in {"Tesco", "Sainsburys", "Morrisons", "M&S"} else None
            yield ScrapedItem(
                name=name,
                price=price,
                category=category,
                retailer=self.retailer,
                loyalty_price=loyalty_price,
                promotion="Price matched" if index in {0, 1} else None,
                image_url=POC_IMAGE[key],
                product_url=f"https://www.{self.retailer.lower().replace('&','and').replace(' ','')}.com/",
                affiliate_url=f"https://www.{self.retailer.lower().replace('&','and').replace(' ','')}.com/?utm_source=comparethebasket",
            )
