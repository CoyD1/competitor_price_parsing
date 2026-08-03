import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI

from routers import competitors, offers, products

app = FastAPI()

app.include_router(products.router)
app.include_router(competitors.router)
app.include_router(offers.router)