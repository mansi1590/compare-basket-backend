from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    retailer: str
    category: str
    price: float
    brand: Optional[str] = None
    size: Optional[str] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    loyalty_price: Optional[float] = None
    loyalty_scheme: Optional[str] = None
    promotion: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    affiliate_url: Optional[str] = None
    match_confidence: float = Field(default=1.0, ge=0, le=1)
    source: Optional[str] = "manual"


class ProductResponse(ProductCreate):
    id: int
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class GroupedProductResponse(BaseModel):
    id: int
    name: str
    category: str
    cheapest_price: float
    highest_price: float
    saving: float
    retailer_count: int
    best_retailers: list[str]
    image_url: str | None = None
    promotion: str | None = None
    updated_at: datetime | None = None


class PriceComparison(BaseModel):
    product_id: int | None = None
    retailer: str
    price: float
    loyalty_price: Optional[float] = None
    effective_price: float
    category: Optional[str] = None
    unit_price: Optional[float] = None
    promotion: Optional[str] = None
    product_url: Optional[str] = None
    affiliate_url: Optional[str] = None
    image_url: Optional[str] = None


class ComparisonResponse(BaseModel):
    product: str
    prices: list[PriceComparison]
    cheapest: str
    saving: float


class BasketCompareRequest(BaseModel):
    items: list[str]
    use_loyalty: bool = False


class BasketCompareResponse(BaseModel):
    totals: dict[str, float]
    cheapest: str
    saving: float
    missing_items: dict[str, list[str]] = {}


class ProductPriceDetail(PriceComparison):
    pass


class ProductDetailResponse(BaseModel):
    product: str
    prices: list[ProductPriceDetail]
    cheapest: str
    cheapest_price: float
    highest_price: float
    saving: float


class SmartBasketItem(BaseModel):
    item: str
    product: str
    retailer: str
    price: float
    loyalty_price: Optional[float] = None
    effective_price: float


class SmartBasketResponse(BaseModel):
    recommended_items: list[SmartBasketItem]
    best_total: float
    saving: float = 0


class RetailerResponse(BaseModel):
    retailer: str
    loyalty_scheme: Optional[str] = None


class PromotionResponse(BaseModel):
    product_id: int
    product: str
    retailer: str
    price: float
    loyalty_price: Optional[float] = None
    promotion: Optional[str] = None


class AffiliateClickCreate(BaseModel):
    product_id: Optional[int] = None
    retailer: str
    affiliate_url: Optional[str] = None
    source: str = "mobile-app"


class UserCreate(BaseModel):
    email: str
    name: Optional[str] = None
    provider: str = "email"


class GoogleLoginRequest(BaseModel):
    email: str
    name: Optional[str] = None
    google_sub: Optional[str] = None
    consent_affiliate: bool = True
    consent_cookies: bool = True


class ConsentCreate(BaseModel):
    user_id: Optional[int] = None
    consent_type: str
    accepted: bool
    country: Optional[str] = None


class PriceHistoryResponse(BaseModel):
    date: datetime | None
    price: float
    loyalty_price: Optional[float] = None
    promotion: Optional[str] = None
