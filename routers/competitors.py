from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Competitor
from schemas import CompetitorCreate, CompetitorResponse
from services.competitors import create_competitor

router = APIRouter(
    prefix="/competitors",
    tags=["competitors"],
)

@router.post("/", response_model=CompetitorResponse)
async def create_competitor_endpoint(
    competitor: CompetitorCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_competitor(db=db, competitor_data=competitor)

@router.get("/", response_model=list[CompetitorResponse])
async def read_competitors(
    db: AsyncSession = Depends(get_db)
):
    query = select(Competitor)
    result = await db.execute(query)
    competitors = result.scalars().all()

    return competitors