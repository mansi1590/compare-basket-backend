from datetime import datetime, timedelta

from models import (
    PriceHistory,
    Product,
    ProductMatch,
    RawScrapedProduct,
    RetailerLocation,
    ScrapeRun,
)
from scraper.mock_scraper import MockRetailerScraper
from scraper.normalizer import canonical_name, match_confidence

RETAILERS = [
    "Tesco",
    "ASDA",
    "Morrisons",
    "Sainsburys",
    "M&S",
    "DMart",
    "JioMart",
    "Blinkit",
    "BigBasket",
]

DEMO_LOCATIONS = [
    ("uk", "cv31", "Royal Leamington Spa", "Warwickshire", "Tesco", "Clubcard"),
    ("uk", "cv31", "Royal Leamington Spa", "Warwickshire", "ASDA", None),
    ("uk", "cv31", "Royal Leamington Spa", "Warwickshire", "Morrisons", "More Card"),
    ("uk", "cv31", "Royal Leamington Spa", "Warwickshire", "Sainsburys", "Nectar"),
    ("uk", "cv31", "Royal Leamington Spa", "Warwickshire", "M&S", "Sparks"),
    ("uk", "cv32", "Royal Leamington Spa", "Warwickshire", "Tesco", "Clubcard"),
    ("uk", "cv32", "Royal Leamington Spa", "Warwickshire", "ASDA", None),
    ("uk", "cv32", "Royal Leamington Spa", "Warwickshire", "Morrisons", "More Card"),
    ("uk", "cv32", "Royal Leamington Spa", "Warwickshire", "Sainsburys", "Nectar"),
    ("uk", "cv32", "Royal Leamington Spa", "Warwickshire", "M&S", "Sparks"),
    ("india", "400701", "Navi Mumbai", "Airoli", "DMart", "DMart Ready"),
    ("india", "400701", "Navi Mumbai", "Airoli", "JioMart", "JioMart"),
    ("india", "400701", "Navi Mumbai", "Airoli", "Blinkit", None),
    ("india", "400701", "Navi Mumbai", "Airoli", "BigBasket", "BB Star"),
]


def get_value(item, key, default=None):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def history_prices(current_price: float, retailer: str):
    today = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
    seed = sum(ord(c) for c in retailer) % 7
    points = [
        (30, current_price + 0.35 + seed * 0.01),
        (20, current_price + 0.25 + seed * 0.01),
        (15, current_price + 0.18),
        (10, current_price + 0.10),
        (5, current_price + 0.05),
        (0, current_price),
    ]
    return [
        (today - timedelta(days=days), round(max(price, 0.01), 2))
        for days, price in points
    ]


def ensure_demo_locations(db):
    for country, code, city, area, retailer, loyalty_scheme in DEMO_LOCATIONS:
        existing = (
            db.query(RetailerLocation)
            .filter(
                RetailerLocation.country.ilike(country),
                RetailerLocation.code.ilike(code),
                RetailerLocation.retailer.ilike(retailer),
            )
            .first()
        )
        if existing:
            existing.city = city
            existing.area = area
            existing.loyalty_scheme = loyalty_scheme
            existing.is_active = True
        else:
            db.add(
                RetailerLocation(
                    country=country,
                    code=code,
                    city=city,
                    area=area,
                    retailer=retailer,
                    loyalty_scheme=loyalty_scheme,
                    is_active=True,
                )
            )
    db.commit()


def upsert_product_from_item(db, item, run_id: int):
    name = get_value(item, "name")
    retailer = get_value(item, "retailer")
    category = get_value(item, "category")
    price = float(get_value(item, "price"))
    loyalty_price = get_value(item, "loyalty_price")
    promotion = get_value(item, "promotion")
    image_url = get_value(item, "image_url")
    product_url = get_value(item, "product_url")
    affiliate_url = get_value(item, "affiliate_url")
    size = get_value(item, "size")
    unit = get_value(item, "unit")
    country = get_value(item, "country", "india" if retailer in {"DMart", "JioMart", "Blinkit", "BigBasket"} else "uk")
    currency = get_value(item, "currency", "INR" if country == "india" else "GBP")

    canonical = canonical_name(name)

    db.query(RawScrapedProduct).filter(
        RawScrapedProduct.retailer.ilike(retailer),
        RawScrapedProduct.raw_name.ilike(name),
    ).delete(synchronize_session=False)

    raw = RawScrapedProduct(
        scrape_run_id=run_id,
        retailer=retailer,
        raw_name=name,
        raw_price=price,
        category=category,
        size=size,
        unit=unit,
        product_url=product_url,
        image_url=image_url,
    )
    db.add(raw)
    db.commit()
    db.refresh(raw)

    product = (
        db.query(Product)
        .filter(Product.name.ilike(canonical), Product.retailer.ilike(retailer))
        .first()
    )

    confidence = match_confidence(name, canonical)

    if not product:
        product = Product(
            name=canonical,
            retailer=retailer,
            category=category,
            price=price,
            country=country,
            currency=currency,
            loyalty_price=loyalty_price,
            promotion=promotion,
            image_url=image_url,
            product_url=product_url,
            affiliate_url=affiliate_url,
            match_confidence=confidence,
            source="mock_scraper",
        )
        db.add(product)
        db.commit()
        db.refresh(product)
    else:
        product.category = category
        product.price = price
        product.country = country
        product.currency = currency
        product.loyalty_price = loyalty_price
        product.promotion = promotion
        product.image_url = image_url or product.image_url
        product.product_url = product_url or product.product_url
        product.affiliate_url = affiliate_url or product.affiliate_url
        product.match_confidence = confidence
        product.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(product)

    db.query(PriceHistory).filter(
        PriceHistory.product_id == product.id,
        PriceHistory.retailer.ilike(retailer),
    ).delete(synchronize_session=False)

    db.query(ProductMatch).filter(
        ProductMatch.product_id == product.id,
        ProductMatch.retailer.ilike(retailer),
    ).delete(synchronize_session=False)

    for observed_at, history_price in history_prices(price, retailer):
        db.add(
            PriceHistory(
                product_id=product.id,
                retailer=retailer,
                price=history_price,
                loyalty_price=loyalty_price,
                promotion=promotion,
                observed_at=observed_at,
            )
        )

    db.add(
        ProductMatch(
            raw_product_id=raw.id,
            product_id=product.id,
            canonical_name=canonical,
            retailer=retailer,
            confidence=confidence,
            review_status="review" if confidence < 0.85 else "auto_matched",
        )
    )

    db.commit()


def run_mock_pipeline(db):
    ensure_demo_locations(db)
    total = 0
    runs = []

    for retailer in RETAILERS:
        run = ScrapeRun(retailer=retailer, status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        try:
            scraper = MockRetailerScraper(retailer)
            items = scraper.run()
            for item in items:
                upsert_product_from_item(db, item, run.id)

            run.status = "success"
            run.items_found = len(items)
            run.finished_at = datetime.utcnow()
            total += len(items)
        except Exception as exc:
            run.status = "failed"
            run.error_message = str(exc)
            run.finished_at = datetime.utcnow()

        db.commit()
        runs.append(
            {
                "retailer": retailer,
                "status": run.status,
                "items_found": run.items_found,
                "error": run.error_message,
            }
        )

    return {"completed": True, "total_items": total, "runs": runs}
