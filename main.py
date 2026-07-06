from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db, engine, Base
from models import Product
from schemas import ProductCreate, ProductResponse

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/products/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_product = Product(
        name=product.name,
        price=product.price,
        url=product.url
    )
    db_add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=list[ProductResponse])
async def read_product(
db: AsyncSession = Depends(get_db)
):
    query = select(Product)
    result = await db.execute(query)
    products = result.scalars().all()
    return products

@app.get("/products/{products_id}", response_model=ProductResponse)
async def read_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product