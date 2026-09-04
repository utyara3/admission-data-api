from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.contest_lists import router as university_router
from src.core.database import get_db
from src.core.logger_config import setup_logger


@asynccontextmanager
async def lifespan(app):
    setup_logger("main")
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(university_router)


@app.get("/")
async def root():
    return {"status": 200}


@app.get("/health")
async def health(db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(text("SELECT 1"))

    return {"status": "healthy", "database": "connected", "result": res.scalar()}
