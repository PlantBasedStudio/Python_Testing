import pytest
from flask import Flask
from server import purchasePlaces, clubs, competitions

def fake_render_template(template_name, **context):
    return {"template": template_name, "context": context}

@pytest.fixture
def setup_env(monkeypatch):
    fake_clubs = [{"name": "Test Club", "email": "test@club.com", "points": "15"}]
    fake_comps = [{"name": "Test Competition", "date": "2099-01-01 10:00:00", "numberOfPlaces": "10"}]
    monkeypatch.setattr("server.clubs", fake_clubs)
    monkeypatch.setattr("server.competitions", fake_comps)
    monkeypatch.setattr("server.render_template", fake_render_template)
    return fake_clubs, fake_comps

def test_purchase_too_many_places_returns_error(setup_env):
    clubs, competitions = setup_env
    app = Flask(__name__)
    app.secret_key = "test_secret"
    with app.test_request_context(method="POST", data={
        "club": "Test Club", "competition": "Test Competition", "places": "15"
    }):
        response, status = purchasePlaces()
        assert status == 400
        assert "Not enough places available in this competition" in response["context"]["error"]