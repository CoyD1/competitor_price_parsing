import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CompetitorOffer, PriceCheck
from parser.price_parser import (
    extract_price_from_html,
    fetch_html_with_browser,
    fetch_price_from_url,
)


async def get_offer_or_404(
        db: AsyncSession,
        offer_id: int,
) -> CompetitorOffer:
    query = select(CompetitorOffer).where(CompetitorOffer.id==offer_id)
    result = await db.execute(query)
    offer = result.scalar_one_or_none()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    return offer

async def create_price_check(
        db: AsyncSession,
        offer: CompetitorOffer,
        status: str,
        price: int | None = None,
        error_message: str | None = None,
) -> PriceCheck:
    price_check = PriceCheck(
        offer_id=offer.id,
        status=status,
        price=price,
        error_message=error_message,
    )

    db.add(price_check)
    await db.commit()
    await db.refresh(price_check)

    return price_check

async def check_offer_price(
    db: AsyncSession,
    offer_id: int,
) -> PriceCheck:
    offer = await get_offer_or_404(db, offer_id)

    if not offer.is_active:
        raise HTTPException(status_code=400, detail="Offer is not active")

    if offer.parser_type not in ("html", "browser"):
        return await create_price_check(
            db=db,
            offer=offer,
            status="blocked",
            error_message=f"Parser type '{offer.parser_type}' is not supported yet",
        )

    if not offer.price_selector:
        return await create_price_check(
            db=db,
            offer=offer,
            status="selector_not_found",
            error_message="Offer price selector is not set",
        )

    try:
        if offer.parser_type == "html":
            parsed_price = await fetch_price_from_url(
                url=offer.url,
                price_selector=offer.price_selector,
            )
        else:
            html = await fetch_html_with_browser(offer.url)
            parsed_price = extract_price_from_html(html, offer.price_selector)

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        status = "blocked" if status_code in (401, 403) else "network_error"

        return await create_price_check(
            db=db,
            offer=offer,
            status=status,
            error_message=f"Product page returned status {status_code}",
        )

    except httpx.RequestError as error:
        return await create_price_check(
            db=db,
            offer=offer,
            status="network_error",
            error_message=f"Failed to fetch product page: {error.__class__.__name__}",
        )

    except ValueError as error:
        return await create_price_check(
            db=db,
            offer=offer,
            status="price_not_found",
            error_message=str(error),
        )

    return await create_price_check(
        db=db,
        offer=offer,
        status="success",
        price=parsed_price,
    )