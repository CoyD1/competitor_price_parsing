from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import CompetitorOffer, PriceCheck
from schemas import (
    CompetitorOfferCreate,
    CompetitorOfferResponse,
    CompetitorOfferUpdate,
    ManualPriceCheckCreate,
    PriceCheckResponse,
)
from services.competitors import create_competitor_offer, update_competitor_offer
from services.offers import check_offer_price, create_manual_offer_price_check, get_offer_or_404

router = APIRouter(
    prefix="/offers",
    tags=["offers"],
)

@router.post("/", response_model=CompetitorOfferResponse)
async def create_competitor_offer_endpoint(
    offer: CompetitorOfferCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_competitor_offer(db=db, offer_data=offer)

@router.get("/", response_model=list[CompetitorOfferResponse])
async def read_competitor_offers(
    db: AsyncSession = Depends(get_db),
):
    query = select(CompetitorOffer)
    result = await db.execute(query)
    offers = result.scalars().all()

    return offers

@router.get("/product/{product_id}", response_model=list[CompetitorOfferResponse])
async def read_product_competitor_offers(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    query = select(CompetitorOffer).where(CompetitorOffer.product_id == product_id)
    result = await db.execute(query)
    offers = result.scalars().all()

    return offers

@router.post("/{offer_id}/check-price", response_model=PriceCheckResponse)
async def check_offer_price_endpoint(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await check_offer_price(db=db, offer_id=offer_id)

@router.post("/{offer_id}/manual-price-check", response_model=PriceCheckResponse)
async def create_manual_offer_price_check_price_endpoint(
    offer_id: int,
    price_check: ManualPriceCheckCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_manual_offer_price_check(
        db=db,
        offer_id=offer_id,
        price_check_data=price_check,
    )

@router.get("/{offer_id}/price-checks", response_model=list[PriceCheckResponse])
async def read_offer_price_checks(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
):
    await get_offer_or_404(db, offer_id)

    query = (
        select(PriceCheck)
        .where(PriceCheck.offer_id == offer_id)
        .order_by(PriceCheck.checked_at.desc())
    )
    result = await db.execute(query)
    price_checks = result.scalars().all()

    return price_checks

@router.patch("/{offer_id}", response_model=CompetitorOfferResponse)
async def update_competitor_offer_endpoint(
    offer_id: int,
    offer_update: CompetitorOfferUpdate,
    db: AsyncSession = Depends(get_db),
):
    offer = await get_offer_or_404(db, offer_id)

    return await update_competitor_offer(
        db=db,
        offer=offer,
        offer_data=offer_update,
    )

@router.delete("/{offer_id}")
async def delete_competitor_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
):
    offer = await get_offer_or_404(db, offer_id)

    await db.delete(offer)
    await db.commit()

    return {"message": "Offer deleted successfully"}