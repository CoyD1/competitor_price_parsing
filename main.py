from fastapi import FastAPI

from database import engine, Base
from routers import products

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(products.router)