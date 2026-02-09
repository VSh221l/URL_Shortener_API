import pytest
from fastapi.testclient import TestClient
import os
from main import app
from database import init_db

TEST_DATABASE = "test_urls.db"

# --- Фикстура для TestClient ---
@pytest.fixture(scope="function") # scope="function" означает, что клиент создается для каждого теста
def client(tmp_path):
    db_path = tmp_path / "test_urls.db"

    os.environ["DATABASE_PATH"] = str(db_path)

    init_db()
    with TestClient(app) as c:
        yield c
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)

# --- Тесты ---
@pytest.mark.asyncio
async def test_shorten_and_redirect(client): # Передаем фикстуру client как аргумент
    """
    Тестирование сокращения URL и последующего редиректа.
    """
    original_url = "https://www.example.com"

    # Тест сокращения
    response = client.post("/shorten", json={"url": original_url})
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    short_url = data["short_url"]
    # Получаем код из URL, возвращенного сервером (например, http://testserver/abc123)
    # TestClient использует http://testserver как базовый URL
    code = short_url.split("/")[-1]

    # Тест редиректа (GET-запрос не следует за редиректами по умолчанию)
    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 307 # 307 Temporary Redirect
    assert response.headers["location"] == original_url

@pytest.mark.asyncio
async def test_redirect_not_found(client): # Передаем фикстуру client как аргумент
    """
    Тестирование ошибки 404 при попытке редиректа по несуществующему коду.
    """
    response = client.get("/nonexistentcode")
    assert response.status_code == 404
    assert response.json() == {"detail": "URL not found"}