from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from . import models, schemas

async def bulk_insert(db: AsyncSession, bulk: schemas.BulkCreate):
    # Méthode DE pro : bulk insert, pas de boucle
    objects = [
        models.DataEvent(
            source=e.source,
            event_type=e.event_type,
            user_id=e.user_id,
            amount=e.amount,
            payload=e.payload
        ) for e in bulk.events
    ]
    db.add_all(objects)
    await db.flush()
    return len(objects)

async def get_events(db: AsyncSession, source: str = None, limit: int = 100, offset: int = 0):
    query = select(models.DataEvent).order_by(models.DataEvent.created_at.desc())
    if source:
        query = query.where(models.DataEvent.source == source)
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()

async def get_stats(db: AsyncSession):
    query = select(
        models.DataEvent.source,
        func.count().label("total"),
        func.sum(models.DataEvent.amount).label("total_amount")
    ).group_by(models.DataEvent.source)
    result = await db.execute(query)
    return result.all()
