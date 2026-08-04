from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Competitor, CompetitorOffer
from schemas import CompetitorCreate, CompetitorOfferCreate, CompetitorOfferUpdate, CompetitorUpdate
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

async def update_competitor_offer(
        db: AsyncSession,
        offer: CompetitorOffer,
        offer_data: CompetitorOfferUpdate,
) -> CompetitorOffer:
    update_data = offer_data.model_dump(exclude_unset=True)

    if "product_id" in update_data:
        await get_product_or_404(db, update_data["product_id"])

    if "competitor_id" in update_data:
        await get_competitor_or_404(db, update_data["competitor_id"])

    if "url" in update_data and update_data["url"] is not None:
        update_data["url"] = str(update_data["url"])

    for field, value in update_data.items():
        setattr(offer, field, value)

    await db.commit()
    await db.refresh(offer)

    return offer

async def update_competitor(
    db: AsyncSession,
    competitor: Competitor,
    competitor_data: CompetitorUpdate,
) -> Competitor:
    update_data = competitor_data.model_dump(exclude_unset=True)

    if "website_url" in update_data and update_data["website_url"] is not None:
        update_data["website_url"] = str(update_data["website_url"])

    for field, value in update_data.items():
        setattr(competitor, field, value)

    await db.commit()
    await db.refresh(competitor)

    return competitor