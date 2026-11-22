from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

# On crée un faux client qui appelle ton API sans lancer uvicorn
client = TestClient(app)

def test_health():
    # 1. On appelle /health comme le ferait curl
    response = client.get("/health")
    # 2. On vérifie que ça répond 200 OK
    assert response.status_code == 200
    # 3. On vérifie le contenu exact
    assert response.json() == {"status": "ok", "service": "data-ingest-api"}

def test_api_key_is_configured():
    # On vérifie que la clé API vient bien du .env et n'est pas vide
    assert settings.API_KEY is not None
    assert len(settings.API_KEY) > 10
