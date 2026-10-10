VALID = {"name": "Ravi Kumar", "course": "Python Programming", "date": "2026-10-10"}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_single_certificate_returns_pdf(client):
    response = client.post("/certificates/single", json=VALID)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_single_missing_field(client):
    payload = {"name": "pasupula supriya", "date": "2026-10-10"}
    response = client.post("/certificates/single", json=payload)
    assert response.status_code == 422


def test_single_empty_name(client):
    response = client.post("/certificates/single", json={**VALID, "name": "   "})
    assert response.status_code == 422


def test_single_invalid_date(client):
    response = client.post("/certificates/single", json={**VALID, "date": "abc"})
    assert response.status_code == 422