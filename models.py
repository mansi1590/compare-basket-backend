from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    retailer = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    country = Column(String, index=True, nullable=True)
    currency = Column(String, nullable=True)

    brand = Column(String, nullable=True)
    size = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    unit_price = Column(Float, nullable=True)
    loyalty_price = Column(Float, nullable=True)
    loyalty_scheme = Column(String, nullable=True)
    promotion = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    product_url = Column(String, nullable=True)
    affiliate_url = Column(String, nullable=True)
    match_confidence = Column(Float, default=1.0)
    source = Column(String, default="manual")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("name", "retailer", name="uq_product_name_retailer"),
    )


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)
    retailer = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    loyalty_price = Column(Float, nullable=True)
    promotion = Column(String, nullable=True)
    observed_at = Column(DateTime, default=datetime.utcnow, index=True)


class RetailerLocation(Base):
    __tablename__ = "retailer_locations"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, index=True, nullable=False)
    code = Column(String, index=True, nullable=False)
    city = Column(String, nullable=True)
    area = Column(String, nullable=True)
    retailer = Column(String, index=True, nullable=False)
    loyalty_scheme = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)


class AffiliateClick(Base):
    __tablename__ = "affiliate_clicks"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    retailer = Column(String, index=True, nullable=False)
    affiliate_url = Column(String, nullable=True)
    source = Column(String, default="mobile-app")
    clicked_at = Column(DateTime, default=datetime.utcnow, index=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    provider = Column(String, default="email")  # email/google
    google_sub = Column(String, nullable=True)
    consent_marketing = Column(Boolean, default=False)
    consent_affiliate = Column(Boolean, default=False)
    consent_cookies = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserConsent(Base):
    __tablename__ = "user_consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    consent_type = Column(String, nullable=False)
    accepted = Column(Boolean, default=False)
    country = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id = Column(Integer, primary_key=True, index=True)
    retailer = Column(String, index=True, nullable=False)
    status = Column(String, default="pending")  # pending/running/success/failed
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    items_found = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)


class RawScrapedProduct(Base):
    __tablename__ = "raw_scraped_products"

    id = Column(Integer, primary_key=True, index=True)
    scrape_run_id = Column(Integer, ForeignKey("scrape_runs.id"), nullable=True)
    retailer = Column(String, index=True, nullable=False)
    raw_name = Column(String, nullable=False)
    raw_price = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    size = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    product_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)


class ProductMatch(Base):
    __tablename__ = "product_matches"

    id = Column(Integer, primary_key=True, index=True)
    raw_product_id = Column(Integer, ForeignKey("raw_scraped_products.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    canonical_name = Column(String, nullable=False)
    retailer = Column(String, nullable=False)
    confidence = Column(Float, default=0.8)
    review_status = Column(String, default="auto_matched")  # auto_matched/review/approved/rejected
    created_at = Column(DateTime, default=datetime.utcnow)
