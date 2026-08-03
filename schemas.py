from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(gt=0)

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: int | None = Field(default=None, gt=0)

class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    created_at: datetime

    model_config = {"from_attributes": True}

class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    price: int
    checked_at: datetime

    model_config = {"from_attributes": True}

class PriceCheckCreate(BaseModel):
    price: int = Field(gt=0)

class ProductFetchPreviewResponse(BaseModel):
    product_id: int
    url: str
    price_selector: str
    fetch_mode: str
    status_code: int | None = None
    html_length: int
    selector_found: bool
    price_text: str | None = None
    parsed_price: int | None = None

ParserType = Literal["html", "browser", "manual", "dns_experimental"]
PriceCheckStatus = Literal[
    "success",
    "blocked",
    "selector_not_found",
    "price_not_found",
    "network_error",
    "manual",
]

class CompetitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    website_url: HttpUrl | None = None

class CompetitorResponse(BaseModel):
    id: int
    name: str
    website_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

class CompetitorOfferCreate(BaseModel):
    product_id: int
    competitor_id: int
    url: HttpUrl
    parser_type: ParserType = "html"
    price_selector: str | None = Field(default=None, max_length=255)
    is_active: bool = True

class CompetitorOfferResponse(BaseModel):
    id: int
    product_id: int
    competitor_id: int
    url: str
    parser_type: str
    price_selector: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class PriceCheckResponse(BaseModel):
    id: int
    offer_id: int
    status: str
    price: int | None = None
    error_message: str | None = None
    checked_at: datetime

    model_config = {"from_attributes": True}