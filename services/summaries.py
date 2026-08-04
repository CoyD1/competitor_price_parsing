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
        price_difference = last_price - product.our_price if last_price is not None else None

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

    successful_offers = [
    offer_summary
    for offer_summary in offer_summaries
    if offer_summary.last_price is not None
]

    if not successful_offers:
        min_competitor_price = None
        cheapest_competitor_name = None
        price_difference_from_min = None
        price_position = "no_competitor_prices"
    else:
        cheapest_offer = min(successful_offers, key=lambda offer_summary: offer_summary.last_price)
        min_competitor_price = cheapest_offer.last_price
        cheapest_competitor_name = cheapest_offer.competitor_name
        price_difference_from_min = product.our_price - min_competitor_price

        if price_difference_from_min < 0:
            price_position = "below_competitor"
        elif price_difference_from_min == 0:
            price_position = "same_as_competitor"
        else:
            price_position = "above_competitor"

    return ProductCompetitorSummary(
        product_id=product.id,
        product_name=product.name,
        our_price=product.our_price,
        min_competitor_price=min_competitor_price,
        cheapest_competitor_name=cheapest_competitor_name,
        price_difference_from_min=price_difference_from_min,
        price_position=price_position,
        offers=offer_summaries,
    )