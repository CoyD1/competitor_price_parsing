from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Product
from schemas import ProductCreate


async def get_product_or_404(
    db: AsyncSession,
    product_id: int,
) -> Product:
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


async def create_product(
    db: AsyncSession,
    product_data: ProductCreate,
) -> Product:
    product = Product(
        name=product_data.name,
        our_price=product_data.our_price,
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    return product