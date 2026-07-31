from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

import httpx
from database import get_db
from models import Product, PriceHistory
from schemas import ProductCreate, ProductResponse, ProductUpdate, PriceHistoryResponse, PriceCheckCreate
from services.products import record_price_check
from parser.price_parser import fetch_price_from_url

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_product = Product(
        name=product.name,
        competitor_name=product.competitor_name,
        price=product.price,
        url=str(product.url) if product.url else None,
        price_selector=product.price_selector
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    price_history = PriceHistory(
        product_id=db_product.id,
        price=db_product.price,
        checked_at=datetime.utcnow()
    )

    db.add(price_history)
    await db.commit()
    await db.refresh(db_product)

    return db_product

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
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@router.get("/{product_id}/price-history", response_model=list[PriceHistoryResponse])
async def read_product_price_history(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    product_query = select(Product).where(Product.id == product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
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
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
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
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not product.url:
        raise HTTPException(status_code=400, detail="Product url is not set")
    
    if not product.price_selector:
        raise HTTPException(status_code=400, detail="Product price selector is not set")
    
    try:
        parsed_price = await fetch_price_from_url(
            url=product.url,
            price_selector=product.price_selector
        )
    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        raise HTTPException(
            status_code=502,
            detail=f"Product page returned status {status_code}"
        )
    
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch product page: {error.__class__.__name__}"
        )
    
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    
    return await record_price_check(
        db=db,
        product=product,
        price=parsed_price
    )

@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
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
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.delete(product)
    await db.commit()

    return {"message": "Product deleted successfully"}