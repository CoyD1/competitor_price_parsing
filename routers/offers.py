from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import CompetitorOffer
from schemas import CompetitorOfferCreate, CompetitorOfferResponse
from services.competitors import create_competitor_offer

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