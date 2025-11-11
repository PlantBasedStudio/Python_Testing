import pytest
from server import app

<<<<<<< HEAD
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server import app, loadClubs, loadCompetitions
=======
>>>>>>> bug/pts_updates_not_reflected

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
