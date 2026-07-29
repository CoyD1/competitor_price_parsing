from pydantic import BaseModel
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    price: int
    url: str | None = None

class ProductUpdate(BaseModel):
    name: str | None = None
    price: int | None = None
    url: str | None = None
    
class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
