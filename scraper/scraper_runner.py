from datetime import datetime

from models import PriceHistory, Product, ProductMatch, RawScrapedProduct, ScrapeRun
from scraper.mock_scraper import MockRetailerScraper
from scraper.normalizer import canonical_name, match_confidence

RETAILERS = ["Tesco", "ASDA", "Morrisons", "Sainsburys", "M&S"]


def upsert_product_from_item(db, item, run_id: int):
    canonical = canonical_name(item.name)
    raw = RawScrapedProduct(
        scrape_run_id=run_id,
        retailer=item.retailer,
        raw_name=item.name,
        raw_price=item.price,
        category=item.category,
        size=getattr(item, "size", None),
        unit=getattr(item, "unit", None),
        product_url=item.product_url,
        image_url=item.image_url,
    )
    db.add(raw)
    db.commit()
    db.refresh(raw)

    product = (
        db.query(Product)
        .filter(Product.name.ilike(canonical), Product.retailer.ilike(item.retailer))
        .first()
    )
    confidence = match_confidence(item.name, canonical)
    if not product:
        product = Product(
            name=canonical,
            retailer=item.retailer,
            category=item.category,
            price=item.price,
            loyalty_price=item.loyalty_price,
            promotion=item.promotion,
            image_url=item.image_url,
            product_url=item.product_url,
            affiliate_url=item.affiliate_url,
            match_confidence=confidence,
            source="mock_scraper",
        )
        db.add(product)
        db.commit()
        db.refresh(product)
    else:
        product.price = item.price
        product.loyalty_price = item.loyalty_price
        product.promotion = item.promotion
        product.image_url = item.image_url or product.image_url
        product.product_url = item.product_url or product.product_url
        product.affiliate_url = item.affiliate_url or product.affiliate_url
        product.match_confidence = confidence
        product.updated_at = datetime.utcnow()
        db.commit()

    db.add(
        PriceHistory(
            product_id=product.id,
            retailer=item.retailer,
            price=item.price,
            loyalty_price=item.loyalty_price,
            promotion=item.promotion,
        )
    )
    db.add(
        ProductMatch(
            raw_product_id=raw.id,
            product_id=product.id,
            canonical_name=canonical,
            retailer=item.retailer,
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
        runs.append({"retailer": retailer, "status": run.status, "items_found": run.items_found})
    return {"completed": True, "total_items": total, "runs": runs}
