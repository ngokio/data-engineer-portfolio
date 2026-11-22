import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

# 1. On crée une fausse base SQLite en mémoire (elle disparaît après le test)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

async def override_get_db():
    # C'est la fausse get_db qui remplace la vraie
    async with TestSessionLocal() as session:
        yield session

# On dit à FastAPI : utilise la fausse base pour les tests
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # On crée les tables + on insère 3 fausses lignes
    async def _setup():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with TestSessionLocal() as session:
            session.add_all([
                models.DataEvent(source="shopify", event_type="purchase", user_id=1, amount=100.0, payload={"order": "1"}),
                models.DataEvent(source="shopify", event_type="purchase", user_id=2, amount=200.0, payload={"order": "2"}),
                models.DataEvent(source="stripe", event_type="payment", user_id=3, amount=50.0, payload={"charge": "1"}),
            ])
            await session.commit()
    asyncio.run(_setup())
    yield
    # Nettoyage après les tests
    async def _teardown():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    asyncio.run(_teardown())

def test_stats_returns_correct_counts():
    response = client.get("/stats")
    assert response.status_code == 200
    data = {row["source"]: row for row in response.json()}
    # On vérifie que la logique COUNT + SUM est juste
    assert data["shopify"]["total"] == 2
    assert data["shopify"]["total_amount"] == 300.0
    assert data["stripe"]["total"] == 1
    assert data["stripe"]["total_amount"] == 50.0

def test_data_filter_by_source():
    # On demande QUE du shopify
    response = client.get("/data?source=shopify")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 2
    # Vérifie que tout ce qu'on reçoit est bien du shopify, jamais du stripe
    for row in rows:
        assert row["source"] == "shopify"
