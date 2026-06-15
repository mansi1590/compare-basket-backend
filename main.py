from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import (
    AffiliateClick,
    Base,
    PriceHistory,
    Product,
    ProductMatch,
    RawScrapedProduct,
    RetailerLocation,
    ScrapeRun,
    User,
    UserConsent,
)
from schemas import (
    AffiliateClickCreate,
    BasketCompareRequest,
    BasketCompareResponse,
    ComparisonResponse,
    ConsentCreate,
    GoogleLoginRequest,
    GroupedProductResponse,
    ProductCreate,
    ProductDetailResponse,
    ProductResponse,
    PromotionResponse,
    RetailerResponse,
    SmartBasketResponse,
    UserCreate,
)

app = FastAPI(title="Compare The Basket API", version="0.4.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def parse_retailers(retailers: str) -> list[str]:
    return [r.strip() for r in retailers.split(",") if r.strip()]


def effective_price(product: Product, use_loyalty: bool = False) -> float:
    if use_loyalty and product.loyalty_price is not None:
        return float(product.loyalty_price)
    return float(product.price)


def apply_retailer_filter(query, retailers: str):
    retailer_list = parse_retailers(retailers)
    if retailer_list:
        return query.filter(or_(*[Product.retailer.ilike(r) for r in retailer_list]))
    return query


def product_query(db: Session, text: str = "", retailers: str = ""):
    query = db.query(Product)
    if text and text.strip():
        query = query.filter(Product.name.ilike(f"%{text.strip()}%"))
    return apply_retailer_filter(query, retailers)


def to_price_row(product: Product, use_loyalty: bool = False):
    return {
        "product_id": product.id,
        "retailer": product.retailer,
        "price": product.price,
        "loyalty_price": product.loyalty_price,
        "effective_price": effective_price(product, use_loyalty),
        "category": product.category,
        "unit_price": product.unit_price,
        "promotion": product.promotion,
        "product_url": product.product_url,
        "affiliate_url": product.affiliate_url,
        "image_url": product.image_url,
        "currency": getattr(product, "currency", None),
    }


def grouped_products_from_rows(products: list[Product], use_loyalty: bool = False):
    groups: dict[str, list[Product]] = {}
    for product in products:
        groups.setdefault(product.name.lower(), []).append(product)

    result = []
    for _, items in groups.items():
        prices = [effective_price(p, use_loyalty) for p in items]
        cheapest = min(prices)
        highest = max(prices)
        best_retailers = [p.retailer for p in items if effective_price(p, use_loyalty) == cheapest]
        representative = min(items, key=lambda p: effective_price(p, use_loyalty))
        result.append(
            {
                "id": representative.id,
                "name": representative.name,
                "category": representative.category,
                "cheapest_price": round(cheapest, 2),
                "highest_price": round(highest, 2),
                "saving": round(highest - cheapest, 2),
                "retailer_count": len({p.retailer for p in items}),
                "best_retailers": best_retailers,
                "image_url": representative.image_url,
                "promotion": representative.promotion,
                "updated_at": representative.updated_at,
                "currency": getattr(representative, "currency", None),
            }
        )
    return sorted(result, key=lambda row: (row["category"], row["name"]))


@app.get("/")
def home():
    return {"message": "Compare The Basket API running successfully", "version": "0.4.1"}


@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Product)
        .filter(Product.name.ilike(product.name), Product.retailer.ilike(product.retailer))
        .first()
    )
    if existing:
        for key, value in product.model_dump().items():
            setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        saved_product = existing
    else:
        saved_product = Product(**product.model_dump())
        db.add(saved_product)
        db.commit()
        db.refresh(saved_product)

    db.add(
        PriceHistory(
            product_id=saved_product.id,
            retailer=saved_product.retailer,
            price=saved_product.price,
            loyalty_price=saved_product.loyalty_price,
            promotion=saved_product.promotion,
        )
    )
    db.commit()
    return saved_product


@app.get("/products", response_model=list[ProductResponse])
def get_products(retailers: str = "", db: Session = Depends(get_db)):
    return apply_retailer_filter(db.query(Product), retailers).order_by(Product.category, Product.name, Product.price).all()


@app.get("/products/grouped", response_model=list[GroupedProductResponse])
def get_grouped_products(retailers: str = "", use_loyalty: bool = False, db: Session = Depends(get_db)):
    products = apply_retailer_filter(db.query(Product), retailers).all()
    return grouped_products_from_rows(products, use_loyalty)


@app.get("/search", response_model=list[ProductResponse])
def search_products(query: str, retailers: str = "", db: Session = Depends(get_db)):
    return product_query(db, query, retailers).order_by(Product.price.asc()).all()


@app.get("/search/grouped", response_model=list[GroupedProductResponse])
def search_products_grouped(query: str = "", retailers: str = "", use_loyalty: bool = False, db: Session = Depends(get_db)):
    products = product_query(db, query, retailers).all()
    return grouped_products_from_rows(products, use_loyalty)


@app.get("/products/category", response_model=list[ProductResponse])
def get_products_by_category(category: str, retailers: str = "", db: Session = Depends(get_db)):
    query = db.query(Product).filter(Product.category.ilike(f"%{category}%"))
    return apply_retailer_filter(query, retailers).order_by(Product.price.asc()).all()


@app.get("/products/category/grouped", response_model=list[GroupedProductResponse])
def get_products_by_category_grouped(category: str, retailers: str = "", use_loyalty: bool = False, db: Session = Depends(get_db)):
    query = db.query(Product).filter(Product.category.ilike(f"%{category}%"))
    products = apply_retailer_filter(query, retailers).all()
    return grouped_products_from_rows(products, use_loyalty)


@app.get("/compare", response_model=ComparisonResponse)
def compare_product(product_name: str, retailers: str = "", use_loyalty: bool = False, db: Session = Depends(get_db)):
    products = product_query(db, product_name, retailers).all()
    if not products:
        return {"product": product_name, "prices": [], "cheapest": "Not Found", "saving": 0}

    cheapest_product = min(products, key=lambda p: effective_price(p, use_loyalty))
    highest_product = max(products, key=lambda p: effective_price(p, use_loyalty))
    return {
        "product": product_name,
        "prices": [to_price_row(p, use_loyalty) for p in sorted(products, key=lambda p: effective_price(p, use_loyalty))],
        "cheapest": cheapest_product.retailer,
        "saving": round(effective_price(highest_product, use_loyalty) - effective_price(cheapest_product, use_loyalty), 2),
    }


@app.get("/product/detail", response_model=ProductDetailResponse)
def product_detail(product_name: str, retailers: str = "", use_loyalty: bool = False, db: Session = Depends(get_db)):
    products = product_query(db, product_name, retailers).all()
    if not products:
        return {"product": product_name, "prices": [], "cheapest": "Not Found", "cheapest_price": 0, "highest_price": 0, "saving": 0}

    sorted_products = sorted(products, key=lambda p: effective_price(p, use_loyalty))
    cheapest_product = sorted_products[0]
    highest_product = sorted_products[-1]
    return {
        "product": product_name,
        "prices": [to_price_row(p, use_loyalty) for p in sorted_products],
        "cheapest": cheapest_product.retailer,
        "cheapest_price": effective_price(cheapest_product, use_loyalty),
        "highest_price": effective_price(highest_product, use_loyalty),
        "saving": round(effective_price(highest_product, use_loyalty) - effective_price(cheapest_product, use_loyalty), 2),
    }


@app.get("/product/price-history/by-name")
def get_price_history_by_product_name(
    product_name: str,
    retailers: str = "",
    use_loyalty: bool = False,
    db: Session = Depends(get_db),
):
    """Return append-only price history grouped by retailer for the selected product name.

    The mobile app uses this for retailer-wise price history in the product detail modal.
    It matches all Product rows with the same name across selected retailers, then reads
    their PriceHistory records and groups them by retailer.
    """
    products = product_query(db, product_name, retailers).all()

    if not products:
        return {"product": product_name, "history": {}}

    product_ids = [p.id for p in products]

    rows = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id.in_(product_ids))
        .order_by(PriceHistory.retailer.asc(), PriceHistory.observed_at.asc())
        .all()
    )

    history: dict[str, list[dict]] = {}

    for row in rows:
        retailer = row.retailer or "Unknown"
        price = row.loyalty_price if use_loyalty and row.loyalty_price is not None else row.price

        history.setdefault(retailer, []).append(
            {
                "date": row.observed_at,
                "price": price,
                "normal_price": row.price,
                "loyalty_price": row.loyalty_price,
                "promotion": row.promotion,
            }
        )

    return {"product": product_name, "history": history}


@app.get("/product/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.id == product_id).first()


@app.get("/product/{product_id}/price-history")
def get_price_history(product_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.observed_at.asc())
        .all()
    )
    return [
        {
            "date": row.observed_at,
            "price": row.price,
            "loyalty_price": row.loyalty_price,
            "promotion": row.promotion,
        }
        for row in rows
    ]


@app.post("/basket/compare", response_model=BasketCompareResponse)
def compare_basket(basket: BasketCompareRequest, retailers: str = "", db: Session = Depends(get_db)):
    retailer_totals: dict[str, float] = {}
    missing_items: dict[str, list[str]] = {}
    retailer_list = parse_retailers(retailers)

    for item in basket.items:
        products = product_query(db, item, retailers).all()
        found_retailers = {p.retailer for p in products}
        if retailer_list:
            missing = [r for r in retailer_list if r not in found_retailers]
            if missing:
                missing_items[item] = missing
        for product in products:
            retailer_totals[product.retailer] = retailer_totals.get(product.retailer, 0) + effective_price(product, basket.use_loyalty)

    if not retailer_totals:
        return {"totals": {}, "cheapest": "Not Found", "saving": 0, "missing_items": missing_items}

    retailer_totals = {retailer: round(total, 2) for retailer, total in retailer_totals.items()}
    cheapest_retailer = min(retailer_totals, key=retailer_totals.get)
    saving = round(max(retailer_totals.values()) - retailer_totals[cheapest_retailer], 2)
    return {"totals": retailer_totals, "cheapest": cheapest_retailer, "saving": saving, "missing_items": missing_items}


@app.post("/basket/smart-recommendation", response_model=SmartBasketResponse)
def smart_basket_recommendation(basket: BasketCompareRequest, retailers: str = "", db: Session = Depends(get_db)):
    recommended_items = []
    best_total = 0.0
    for item in basket.items:
        products = product_query(db, item, retailers).all()
        if not products:
            continue
        cheapest = min(products, key=lambda p: effective_price(p, basket.use_loyalty))
        price = effective_price(cheapest, basket.use_loyalty)
        recommended_items.append(
            {
                "item": item,
                "product": cheapest.name,
                "retailer": cheapest.retailer,
                "price": cheapest.price,
                "loyalty_price": cheapest.loyalty_price,
                "effective_price": price,
            }
        )
        best_total += price

    single_retailer = compare_basket(basket, retailers, db)
    saving = max(0, round(single_retailer.saving if hasattr(single_retailer, "saving") else single_retailer.get("saving", 0), 2))
    return {"recommended_items": recommended_items, "best_total": round(best_total, 2), "saving": saving}


@app.get("/retailers", response_model=list[RetailerResponse])
def get_retailers(country: str = "", db: Session = Depends(get_db)):
    query = db.query(RetailerLocation)
    if country:
        query = query.filter(RetailerLocation.country.ilike(country))
    rows = query.filter(RetailerLocation.is_active.is_(True)).all()
    if rows:
        return [{"retailer": r.retailer, "loyalty_scheme": r.loyalty_scheme} for r in rows]
    product_rows = db.query(Product.retailer).distinct().order_by(Product.retailer).all()
    return [{"retailer": row[0], "loyalty_scheme": None} for row in product_rows]


@app.get("/retailers/by-location")
def get_retailers_by_location(country: str, code: str, db: Session = Depends(get_db)):
    normal_country = country.strip().lower()
    normal_code = code.strip().lower().replace(" ", "")
    retailers = (
        db.query(RetailerLocation)
        .filter(
            RetailerLocation.country.ilike(normal_country),
            func.lower(func.replace(RetailerLocation.code, " ", "")).like(f"{normal_code}%"),
            RetailerLocation.is_active.is_(True),
        )
        .all()
    )

    fallback = False
    if not retailers:
        fallback = True
        retailers = (
            db.query(RetailerLocation)
            .filter(RetailerLocation.country.ilike(normal_country), RetailerLocation.is_active.is_(True))
            .limit(6)
            .all()
        )

    return {
        "country": normal_country,
        "code": code,
        "fallback": fallback,
        "message": "Showing demo retailers for this country" if fallback else "Retailers available near this location",
        "retailers": list(set(r.retailer for r in retailers)),
        "loyalty_schemes": {r.retailer: r.loyalty_scheme for r in retailers if r.loyalty_scheme},
    }


@app.get("/search/suggestions")
def search_suggestions(q: str = Query(default=""), db: Session = Depends(get_db)):
    if not q.strip():
        return []
    rows = db.query(Product.name).filter(Product.name.ilike(f"%{q}%")).distinct().limit(8).all()
    return [row[0] for row in rows]


@app.get("/promotions", response_model=list[PromotionResponse])
def get_promotions(retailer: str = "", db: Session = Depends(get_db)):
    query = db.query(Product).filter(Product.promotion.isnot(None))
    if retailer:
        query = query.filter(Product.retailer.ilike(retailer))
    products = query.order_by(Product.retailer, Product.name).all()
    return [
        {
            "product_id": p.id,
            "product": p.name,
            "retailer": p.retailer,
            "price": p.price,
            "loyalty_price": p.loyalty_price,
            "promotion": p.promotion,
        }
        for p in products
    ]


@app.post("/affiliate/click")
def track_affiliate_click(payload: AffiliateClickCreate, db: Session = Depends(get_db)):
    click = AffiliateClick(**payload.model_dump())
    db.add(click)
    db.commit()
    db.refresh(click)
    return {"tracked": True, "click_id": click.id}


@app.post("/auth/register")
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        return {"user_id": existing.id, "email": existing.email, "created": False}
    user = User(email=payload.email, name=payload.name, provider=payload.provider)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "email": user.email, "created": True}


@app.post("/auth/google-login")
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        user = User(email=payload.email, name=payload.name, provider="google", google_sub=payload.google_sub)
        db.add(user)
        db.commit()
        db.refresh(user)
    user.consent_affiliate = payload.consent_affiliate
    user.consent_cookies = payload.consent_cookies
    db.commit()
    return {"user_id": user.id, "email": user.email, "name": user.name, "provider": user.provider, "token": f"poc-token-{user.id}"}


@app.post("/consent/save")
def save_consent(payload: ConsentCreate, db: Session = Depends(get_db)):
    consent = UserConsent(**payload.model_dump())
    db.add(consent)
    db.commit()
    db.refresh(consent)
    return {"saved": True, "consent_id": consent.id}


@app.get("/admin/stats")
def admin_stats(db: Session = Depends(get_db)):
    grouped_rows = db.query(Product.name).distinct().all()

    price_gap_percentages = []
    saving_amounts = []

    for row in grouped_rows:
        name = row[0]
        prices = [float(p.price) for p in db.query(Product).filter(Product.name.ilike(name)).all() if p.price is not None]
        if len(prices) < 2:
            continue

        lowest = min(prices)
        highest = max(prices)

        if lowest > 0:
            price_gap_percentages.append(((highest - lowest) / lowest) * 100)
        saving_amounts.append(highest - lowest)

    latest_price_observation = db.query(func.max(PriceHistory.observed_at)).scalar()
    latest_product_update = db.query(func.max(Product.updated_at)).scalar()
    last_scraped_at = latest_price_observation or latest_product_update

    average_price_gap_percent = (
        round(sum(price_gap_percentages) / len(price_gap_percentages), 2)
        if price_gap_percentages
        else 0
    )
    average_saving_amount = (
        round(sum(saving_amounts) / len(saving_amounts), 2)
        if saving_amounts
        else 0
    )

    total_matches = db.query(ProductMatch).count()
    confident_matches = db.query(ProductMatch).filter(ProductMatch.confidence >= 0.8).count()
    match_confidence_rate = round((confident_matches / total_matches) * 100, 2) if total_matches else 100

    total_products = db.query(Product).count()
    freshness_cutoff = datetime.utcnow() - timedelta(hours=24)
    fresh_products = db.query(Product).filter(Product.updated_at >= freshness_cutoff).count()
    data_freshness_percent = round((fresh_products / total_products) * 100, 1) if total_products else 100

    category_rows = (
        db.query(Product.category, func.count(Product.id))
        .group_by(Product.category)
        .order_by(Product.category)
        .all()
    )
    category_coverage = [
        {
            "label": category or "Uncategorised",
            "count": count,
        }
        for category, count in category_rows
    ]

    return {
        "retailers": db.query(Product.retailer).distinct().count(),
        "products": db.query(Product).count(),
        "grouped_products": db.query(Product.name).distinct().count(),
        "price_observations": db.query(PriceHistory).count(),
        "affiliate_clicks": db.query(AffiliateClick).count(),
        "users": db.query(User).count(),
        "scrape_runs": db.query(ScrapeRun).count(),
        "low_confidence_matches": db.query(ProductMatch).filter(ProductMatch.confidence < 0.8).count(),
        "average_price_gap_percent": average_price_gap_percent,
        "average_saving_amount": average_saving_amount,
        "match_confidence_rate": match_confidence_rate,
        "data_freshness_percent": data_freshness_percent,
        "last_scraped_at": last_scraped_at,
        "category_coverage": category_coverage,
    }


@app.get("/admin/scraper/status")
def scraper_status(db: Session = Depends(get_db)):
    rows = db.query(ScrapeRun).order_by(ScrapeRun.started_at.desc()).limit(20).all()
    return [
        {
            "id": row.id,
            "retailer": row.retailer,
            "status": row.status,
            "started_at": row.started_at,
            "finished_at": row.finished_at,
            "items_found": row.items_found,
            "error_message": row.error_message,
        }
        for row in rows
    ]


@app.get("/admin/matching-queue")
def matching_queue(db: Session = Depends(get_db)):
    rows = db.query(ProductMatch).filter(ProductMatch.confidence < 0.85).order_by(ProductMatch.created_at.desc()).limit(50).all()
    return [
        {
            "id": row.id,
            "canonical_name": row.canonical_name,
            "retailer": row.retailer,
            "confidence": row.confidence,
            "review_status": row.review_status,
        }
        for row in rows
    ]


@app.post("/admin/matching-queue/{match_id}/approve")
def approve_match(match_id: int, db: Session = Depends(get_db)):
    row = db.query(ProductMatch).filter(ProductMatch.id == match_id).first()
    if not row:
        return {"updated": False, "message": "Match not found"}
    row.review_status = "approved"
    db.commit()
    return {"updated": True, "match_id": match_id, "review_status": row.review_status}


@app.post("/admin/matching-queue/{match_id}/reject")
def reject_match(match_id: int, db: Session = Depends(get_db)):
    row = db.query(ProductMatch).filter(ProductMatch.id == match_id).first()
    if not row:
        return {"updated": False, "message": "Match not found"}
    row.review_status = "rejected"
    db.commit()
    return {"updated": True, "match_id": match_id, "review_status": row.review_status}


@app.post("/scraper/run-mock")
def run_mock_scraper(db: Session = Depends(get_db)):
    from scraper.scraper_runner import run_mock_pipeline

    result = run_mock_pipeline(db)
    return result
