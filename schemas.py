from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from constants import ParserType


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    our_price: int = Field(gt=0)

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    our_price: int | None = Field(default=None, gt=0)

class ProductResponse(BaseModel):
    id: int
    name: str
    our_price: int
    created_at: datetime

    model_config = {"from_attributes": True}

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

class CompetitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    website_url: HttpUrl | None = None

class CompetitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
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
    parser_type: ParserType = ParserType.HTML
    price_selector: str | None = Field(default=None, max_length=255)
    is_active: bool = True

class CompetitorOfferUpdate(BaseModel):
    product_id: int | None = None
    competitor_id: int | None = None
    url: HttpUrl | None = None
    parser_type: ParserType | None = None
    price_selector: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None

class CompetitorOfferResponse(BaseModel):
    id: int
    product_id: int
    competitor_id: int
    url: str
    parser_type: ParserType
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

class ManualPriceCheckCreate(BaseModel):
    price: int = Field(gt=0)

class CompetitorOfferSummary(BaseModel):
    offer_id: int
    competitor_id: int
    competitor_name: str
    url: str
    parser_type: ParserType
    is_active: bool
    last_status: str | None = None
    last_price: int | None = None
    price_difference: int | None = None
    checked_at: datetime | None = None

class ProductCompetitorSummary(BaseModel):
    product_id: int
    product_name: str
    our_price: int
    min_competitor_price: int | None = None
    cheapest_competitor_name: str | None = None
    price_difference_from_min: int | None = None
    price_position: str
    offers: list[CompetitorOfferSummary]