from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from models import Product, PriceHistory

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
