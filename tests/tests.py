import pytest
from server import app


@pytest.fixture
def client(monkeypatch):
    fake_clubs = [
        {"name": "Test Club", "email": "test@club.com", "points": "15"},
        {"name": "Other Club", "email": "other@club.com", "points": "5"}
    ]
    fake_comps = [
        {"name": "Spring Festival", "date": "2099-01-01 10:00:00", "numberOfPlaces": "20"}
    ]

    monkeypatch.setattr("server.clubs", fake_clubs)
    monkeypatch.setattr("server.competitions", fake_comps)

    app.testing = True
    with app.test_client() as c:
        yield c, fake_clubs, fake_comps