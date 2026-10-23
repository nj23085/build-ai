from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_crack_endpoint_rejects_non_image():
    response = client.post(
        "/api/analyze/cracks",
        files={"image": ("notes.txt", b"not an image", "text/plain")},
        data={"description": "test upload"},
    )
    assert response.status_code == 415

def test_crack_endpoint_rejects_empty_image():
    response = client.post(
        "/api/analyze/cracks",
        files={"image": ("empty.png", b"", "image/png")},
        data={"description": "empty image"},
    )
    assert response.status_code == 400
