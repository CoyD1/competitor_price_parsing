from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import PriceHistory, Product
from schemas import (
    PriceCheckCreate,
    PriceHistoryResponse,
    ProductCreate,
    ProductFetchPreviewResponse,
    ProductResponse,
    ProductUpdate,
)
from services.products import (
    create_product_with_initial_history,
    get_product_or_404,
    parse_and_record_product_price,
    preview_product_fetch,
    preview_product_fetch_with_browser,
    record_price_check,
)

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate, 
    db: AsyncSession = Depends(get_db)
):
    return await create_product_with_initial_history(db=db, product_data=product)

@router.get("/", response_model=list[ProductResponse])
async def read_products(
    db: AsyncSession = Depends(get_db)
):
    query = select(Product)
    result = await db.execute(query)
    products = result.scalars().all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):   
    return await get_product_or_404(db, product_id)

@router.get("/{product_id}/price-history", response_model=list[PriceHistoryResponse])
async def read_product_price_history(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    await get_product_or_404(db, product_id)
    
    history_query = (
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.checked_at.desc())
    )
    history_result = await db.execute(history_query)
    history = history_result.scalars().all()

    return history

@router.post("/{product_id}/price-check", response_model=ProductResponse)
async def create_product_price_check(
    product_id: int,
    price_check: PriceCheckCreate,
    db: AsyncSession = Depends(get_db)
):
    product = await get_product_or_404(db, product_id)
    
    return await record_price_check(
        db=db,
        product=product,
        price=price_check.price
    )

@router.post("/{product_id}/parse-price", response_model=ProductResponse)
async def parse_product_price(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await parse_and_record_product_price(
        db=db,
        product_id=product_id
    )

@router.post("/{product_id}/fetch-preview", response_model=ProductFetchPreviewResponse)
async def preview_product_fetch_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await preview_product_fetch(
        db=db, 
        product_id=product_id
    )

@router.post("/{product_id}/browser-fetch-preview", response_model=ProductFetchPreviewResponse)
async def preview_product_browser_fetch_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await preview_product_fetch_with_browser(
        db=db,
        product_id=product_id
    )

@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    product = await get_product_or_404(db, product_id)
    
    update_data = product_update.model_dump(exclude_unset=True)
    old_price = product.price
    
    if "url" in update_data and update_data["url"] is not None:
        update_data["url"] = str(update_data["url"])

    for field, value in update_data.items():
        setattr(product, field, value)

    if "price" in update_data and product.price != old_price:
        product.last_checked_at = datetime.utcnow()

        price_history = PriceHistory(
            product_id=product.id,
            price=product.price,
            checked_at=product.last_checked_at
        )
    
        db.add(price_history)

    await db.commit()
    await db.refresh(product)

    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    product = await get_product_or_404(db, product_id)
    
    await db.delete(product)
    await db.commit()

    return {"message": "Product deleted successfully"}