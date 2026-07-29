from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(gt=0)
    url: HttpUrl | None = None

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: int | None = Field(default=None, gt=0)
    url: HttpUrl | None = None

class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
