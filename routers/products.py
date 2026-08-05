from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Product
from schemas import (
    ProductCompetitorSummary,
    ProductCreate,
    ProductOfferChecksResponse,
    ProductResponse,
    ProductUpdate,
)
from services.product_checks import check_product_offers
from services.products import create_product as create_product_service
from services.products import get_product_or_404
from services.summaries import get_product_competitor_summary

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate, 
    db: AsyncSession = Depends(get_db)
):
    return await create_product_service(db=db, product_data=product)

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

@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    product = await get_product_or_404(db, product_id)
    
    update_data = product_update.model_dump(exclude_unset=True) 
    
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return product

@router.get("/{product_id}/competitor-summary", response_model=ProductCompetitorSummary)
async def read_product_competitor_summary(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_product_competitor_summary(db=db, product_id=product_id)

@router.post("/{product_id}/check-offers", response_model=ProductOfferChecksResponse)
async def check_product_offers_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await check_product_offers(db=db, product_id=product_id)

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    product = await get_product_or_404(db, product_id)
    
    await db.delete(product)
    await db.commit()

    return {"message": "Product deleted successfully"}