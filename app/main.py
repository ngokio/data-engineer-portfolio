from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .database import Base, engine, get_db
from . import schemas, crud
from typing import Optional

app = FastAPI(title="DATA INGEST API - Produit vendable", version="1.0.0")

API_KEY = "sk-client-12345"

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API Key invalide")
    return x_api_key

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "data-ingest-api"}

# === INGESTION : Ce que tu vends ===
@app.post("/ingest/bulk", dependencies=[Depends(verify_api_key)])
async def ingest_bulk(bulk: schemas.BulkCreate, db: AsyncSession = Depends(get_db)):
    count = await crud.bulk_insert(db, bulk)
    return {"status": "accepted", "inserted": count}

# === MISE A DISPOSITION : Ce que le client consomme ===
@app.get("/data", response_model=list[schemas.EventRead])
async def list_data(source: Optional[str] = None, limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await crud.get_events(db, source=source, limit=limit, offset=offset)

@app.get("/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    rows = await crud.get_stats(db)
    return [{"source": r.source, "total": r.total, "total_amount": float(r.total_amount or 0)} for r in rows]
