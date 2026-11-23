import sys
from pathlib import Path

# On ajoute la racine du projet (là où il y a le dossier app/) au chemin Python
sys.path.insert(0, str(Path(__file__).parent))

# Après tous les tests, on ferme proprement le moteur Postgres
# Sinon 【entity-GitHub Actions¦canonical_name=GitHub】 reste bloqué et atteint le timeout
import pytest
import asyncio

@pytest.fixture(scope="session", autouse=True)
def close_engine_after_tests():
    yield
    try:
        from app.database import engine
        asyncio.run(engine.dispose())
    except Exception:
        pass
