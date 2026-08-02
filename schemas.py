from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    competitor_name: str | None = Field(default=None, max_length=100)
    price: int = Field(gt=0)
    url: HttpUrl | None = None
    price_selector: str | None = Field(default=None, max_length=255)

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    competitor_name: str | None = Field(default=None, max_length=100)
    price: int | None = Field(default=None, gt=0)
    url: HttpUrl | None = None
    price_selector: str | None = Field(default=None, max_length=255)

class ProductResponse(BaseModel):
    id: int
    name: str
    competitor_name: str | None = None
    price: int
    url: str | None = None
    price_selector: str | None = None
    created_at: datetime
    last_checked_at: datetime | None = None

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
    status_code: int
    html_length: int
    selector_found: bool
    price_text: str | None = None
    parsed_price: int | None = None