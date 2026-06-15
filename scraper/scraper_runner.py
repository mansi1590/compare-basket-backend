from datetime import datetime

from models import PriceHistory, Product, ProductMatch, RawScrapedProduct, ScrapeRun
from scraper.mock_scraper import MockRetailerScraper
from scraper.normalizer import canonical_name, match_confidence

RETAILERS = ["Tesco", "ASDA", "Morrisons", "Sainsburys", "M&S"]


def get_value(item, key, default=None):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def upsert_product_from_item(db, item, run_id: int):
    name = get_value(item, "name")
    retailer = get_value(item, "retailer")
    category = get_value(item, "category")
    price = get_value(item, "price")
    loyalty_price = get_value(item, "loyalty_price")
    promotion = get_value(item, "promotion")
    image_url = get_value(item, "image_url")
    product_url = get_value(item, "product_url")
    affiliate_url = get_value(item, "affiliate_url")
    size = get_value(item, "size")
    unit = get_value(item, "unit")

    canonical = canonical_name(name)

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
        product.price = price
        product.loyalty_price = loyalty_price
        product.promotion = promotion
        product.image_url = image_url or product.image_url
        product.product_url = product_url or product.product_url
        product.affiliate_url = affiliate_url or product.affiliate_url
        product.match_confidence = confidence
        product.updated_at = datetime.utcnow()
        db.commit()

    db.add(
        PriceHistory(
            product_id=product.id,
            retailer=retailer,
            price=price,
            loyalty_price=loyalty_price,
            promotion=promotion,
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