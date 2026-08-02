from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import PriceHistory, Product
from parser.price_parser import extract_price_from_html, fetch_html_from_url, fetch_price_from_url, fetch_html_with_browser
from schemas import ProductCreate, ProductFetchPreviewResponse


async def get_product_or_404(
        db: AsyncSession,
        product_id: int
) -> Product:
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

async def record_price_check(
        db: AsyncSession,
        product: Product,
        price: int
) -> Product:
    checked_at = datetime.utcnow()

    product.price = price
    product.last_checked_at = checked_at

    price_history = PriceHistory(
        product_id=product.id,
        price=price,
        checked_at=checked_at
    )

    db.add(price_history)

    await db.commit()
    await db.refresh(product)
    
    return product

async def create_product_with_initial_history(
    db: AsyncSession,
    product_data: ProductCreate
) -> Product:
    checked_at = datetime.utcnow()

    product = Product(
        name=product_data.name,
        competitor_name=product_data.competitor_name,
        price=product_data.price,
        url=str(product_data.url) if product_data.url else None,
        price_selector=product_data.price_selector,
        last_checked_at=checked_at
    )

    db.add(product)
    await db.flush()

    price_history = PriceHistory(
        product_id=product.id,
        price=product.price,
        checked_at=checked_at
    )

    db.add(price_history)

    await db.commit()
    await db.refresh(product)

    return product

async def parse_and_record_product_price(
        db: AsyncSession,
        product_id: int
) -> Product:
    product = await get_product_or_404(db, product_id)
    
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
        ) from error
    
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch product page: {error.__class__.__name__}"
        ) from error
    
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    
    return await record_price_check(
        db=db,
        product=product,
        price=parsed_price
    )

async def preview_product_fetch(
        db: AsyncSession,
        product_id: int
) -> ProductFetchPreviewResponse:
    product = await get_product_or_404(db, product_id)

    if not product.url:
        raise HTTPException(status_code=400, detail="Product url is not set")
    
    if not product.price_selector:
        raise HTTPException(status_code=400, detail="Product price selector is not set")
    
    try:
        response = await fetch_html_from_url(product.url)
    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        raise HTTPException(
            status_code=502,
            detail=f"Product page returned status {status_code}"
        ) from error
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch product page: {error.__class__.__name__}"
        ) from error
    
    soup = BeautifulSoup(response.text, "html.parser")
    price_element = soup.select_one(product.price_selector)

    if not price_element:
        return ProductFetchPreviewResponse(
            product_id=product.id,
            url=product.url,
            price_selector=product.price_selector,
            fetch_mode="http",
            status_code=response.status_code,
            html_length=len(response.text),
            selector_found=False,
        )
    
    price_text = price_element.get_text(strip=True)

    try:
        parsed_price = extract_price_from_html(response.text, product.price_selector)
    except ValueError:
        parsed_price = None

    return ProductFetchPreviewResponse(
        product_id=product.id,
        url=product.url,
        price_selector=product.price_selector,
        fetch_mode="http",
        status_code=response.status_code,
        html_length=len(response.text),
        selector_found=True,
        price_text=price_text,
        parsed_price=parsed_price,
    )

async def preview_product_fetch_with_browser(
        db: AsyncSession,
        product_id: int
) -> ProductFetchPreviewResponse:
    product = await get_product_or_404(db, product_id)

    if not product.url:
        raise HTTPException(status_code=400, detail="Product url is not set")
    
    if not product.price_selector:
        raise HTTPException(status_code=400, detail="Product price selector is not set")
    
    try:
        html = await fetch_html_with_browser(product.url)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch product page with browser: {error.__class__.__name__}"
        ) from error
    
    soup = BeautifulSoup(html, "html.parser")
    price_element = soup.select_one(product.price_selector)

    if not price_element:
        return ProductFetchPreviewResponse(
            product_id=product.id,
            url=product.url,
            price_selector=product.price_selector,
            fetch_mode="browser",
            status_code=None,
            html_length=len(html),
            selector_found=False,
        )

    price_text = price_element.get_text(strip=True)

    try:
        parsed_price = extract_price_from_html(html, product.price_selector) 
    except ValueError:
        parsed_price = None

    return ProductFetchPreviewResponse(
        product_id=product.id,
        url=product.url,
        price_selector=product.price_selector,
        fetch_mode="browser",
        status_code=None,
        html_length=len(html),
        selector_found=True,
        price_text=price_text,
        parsed_price=parsed_price,
    ) 