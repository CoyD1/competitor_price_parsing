from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Competitor, CompetitorOffer, PriceCheck
from schemas import CompetitorOfferSummary, ProductCompetitorSummary
from services.products import get_product_or_404


async def get_product_competitor_summary(
        db: AsyncSession,
        product_id: int,
) -> ProductCompetitorSummary:
    product = await get_product_or_404(db, product_id)

    offers_query = select(CompetitorOffer).where(CompetitorOffer.product_id == product_id)
    offers_result = await db.execute(offers_query)
    offers = offers_result.scalars().all()

    offer_summaries = []

    for offer in offers:
        competitor_query = select(Competitor).where(Competitor.id == offer.competitor_id)
        competitor_result = await db.execute(competitor_query)
        competitor = competitor_result.scalar_one()

        last_check_query = (
            select(PriceCheck)
            .where(PriceCheck.offer_id == offer.id)
            .order_by(PriceCheck.checked_at.desc())
            .limit(1)
        )
        last_check_result = await db.execute(last_check_query)
        last_check = last_check_result.scalar_one_or_none()

        last_price = last_check.price if last_check else None
        price_difference = last_price - product.price if last_price is not None else None

        offer_summaries.append(
            CompetitorOfferSummary(
                offer_id=offer.id,
                competitor_id=offer.competitor_id,
                competitor_name=competitor.name,
                url=offer.url,
                parser_type=offer.parser_type,
                is_active=offer.is_active,
                last_status=last_check.status if last_check else None,
                last_price=last_price,
                price_difference=price_difference,
                checked_at=last_check.checked_at if last_check else None,
            )
        )

    return ProductCompetitorSummary(
        product_id=product.id,
        product_name=product.name,
        product_price=product.price,
        offers=offer_summaries,
        )