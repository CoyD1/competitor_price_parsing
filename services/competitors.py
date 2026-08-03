from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Competitor, CompetitorOffer
from schemas import CompetitorCreate, CompetitorOfferCreate
from services.products import get_product_or_404


async def get_competitor_or_404(
        db: AsyncSession,
        competitor_id: int,
) -> Competitor:
    query = select(Competitor).where(Competitor.id == competitor_id)
    result = await db.execute(query)
    competitor = result.scalar_one_or_none()

    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    return competitor

async def create_competitor(
        db: AsyncSession,
        competitor_data: CompetitorCreate,
) -> Competitor:
    competitor = Competitor(
        name=competitor_data.name,
        website_url=str(competitor_data.website_url) if competitor_data.website_url else None,
    )

    db.add(competitor)
    await db.commit()
    await db.refresh(competitor)

    return competitor

async def create_competitor_offer(
        db: AsyncSession,
        offer_data: CompetitorOfferCreate,
) -> CompetitorOffer:
    await get_product_or_404(db, offer_data.product_id)
    await get_competitor_or_404(db, offer_data.competitor_id)

    offer = CompetitorOffer(
        product_id=offer_data.product_id,
        competitor_id=offer_data.competitor_id,
        url=str(offer_data.url),
        parser_type=offer_data.parser_type,
        price_selector=offer_data.price_selector,
        is_active=offer_data.is_active,
    )

    db.add(offer)
    await db.commit()
    await db.refresh(offer)

    return offer