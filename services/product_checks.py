from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CompetitorOffer
from schemas import ProductOfferChecksResponse
from services.offers import check_offer_price
from services.products import get_product_or_404


async def check_product_offers(
    db: AsyncSession,
    product_id: int,
) -> ProductOfferChecksResponse:
    await get_product_or_404(db, product_id)

    offers_query = (
        select(CompetitorOffer)
        .where(CompetitorOffer.product_id == product_id)
        .where(CompetitorOffer.is_active.is_(True))
    )
    offers_result = await db.execute(offers_query)
    offers = offers_result.scalars().all()

    checks = []

    for offer in offers:
        price_check = await check_offer_price(db=db, offer_id=offer.id)
        checks.append(price_check)

    return ProductOfferChecksResponse(
        product_id=product_id,
        checked_count=len(checks),
        checks=checks,
    )