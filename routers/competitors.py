from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Competitor
from schemas import CompetitorCreate, CompetitorResponse, CompetitorUpdate
from services.competitors import create_competitor, get_competitor_or_404, update_competitor

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

@router.get("/{competitor_id}", response_model=CompetitorResponse)
async def read_competitor(
    competitor_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_competitor_or_404(db, competitor_id)


@router.patch("/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor_endpoint(
    competitor_id: int,
    competitor_update: CompetitorUpdate,
    db: AsyncSession = Depends(get_db),
):
    competitor = await get_competitor_or_404(db, competitor_id)

    return await update_competitor(
        db=db,
        competitor=competitor,
        competitor_data=competitor_update,
    )


@router.delete("/{competitor_id}")
async def delete_competitor(
    competitor_id: int,
    db: AsyncSession = Depends(get_db),
):
    competitor = await get_competitor_or_404(db, competitor_id)

    await db.delete(competitor)
    await db.commit()

    return {"message": "Competitor deleted successfully"}