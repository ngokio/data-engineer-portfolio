from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from .database import Base, engine, get_db
from . import schemas, crud
from typing import Optional
from .config import settings
import pandas as pd

API_KEY = settings.API_KEY

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API Key invalide")
    return x_api_key

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Data Ingest API - Shopify / Stripe", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "data-ingest-api"}

@app.post("/ingest/bulk", dependencies=[Depends(verify_api_key)])
async def ingest_bulk(bulk: schemas.BulkCreate, db: AsyncSession = Depends(get_db)):
    count = await crud.bulk_insert(db, bulk)
    return {"status": "accepted", "inserted": count}

@app.get("/data", response_model=list[schemas.EventRead])
async def list_data(source: Optional[str] = None, limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await crud.get_events(db, source=source, limit=limit, offset=offset)

@app.get("/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    rows = await crud.get_stats(db)
    return [{"source": r.source, "total": r.total, "total_amount": float(r.total_amount or 0)} for r in rows]

@app.get("/dashboard", tags=["dashboard"])
async def dashboard():
    dashboard_path = Path(__file__).resolve().parent.parent / "dashboard.html"
    return FileResponse(dashboard_path, media_type="text/html")