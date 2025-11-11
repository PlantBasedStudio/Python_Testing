import pytest
from server import purchasePlaces
from flask import Flask
from datetime import datetime, timedelta
import html

def test_booking_past_competition_returns_error(client):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "2",
    }
    response = c.post("/purchasePlaces", data=data)
    decoded = html.unescape(response.get_data(as_text=True))

    assert response.status_code == 400
    assert "terminée" in decoded


def test_booking_future_competition(client):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "3",
    }
    response = c.post("/purchasePlaces", data=data)
    decoded = html.unescape(response.get_data(as_text=True))

    assert response.status_code == 200
    assert "Great-booking complete" in decoded or "welcome" in decoded
    
def test_full_flow_with_past_competition(client):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    response_index = c.get("/")
    assert response_index.status_code == 200

    response_summary = c.post("/showSummary", data={"email": clubs[0]["email"]})
    assert response_summary.status_code == 200

    data = {
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "2",
    }
    response_booking = c.post("/purchasePlaces", data=data)
    decoded = html.unescape(response_booking.get_data(as_text=True))
    assert response_booking.status_code == 400
    assert "terminée" in decoded
    
@pytest.fixture
def mock_templates(monkeypatch):
    def fake_render_template(template_name, **context):
        return f"Rendered {template_name} with {context}"
    monkeypatch.setattr("server.render_template", fake_render_template)


def test_purchase_places_in_past_competition_returns_400(client, monkeypatch, mock_templates):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={
                                                    "club": clubs[0]["name"],
                                                    "competition": competitions[0]["name"],
                                                    "places": "3",
                                                }):
        response, status = purchasePlaces()
        assert status == 400
        assert "terminée" in response


def test_purchase_places_in_future_competition(client, monkeypatch, mock_templates):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")

    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={
                                                    "club": clubs[0]["name"],
                                                    "competition": competitions[0]["name"],
                                                    "places": "5",
                                                }):
        response = purchasePlaces()
        assert "welcome.html" in response
        assert int(competitions[0]["numberOfPlaces"]) == 15

def test_purchase_places_in_past_competition_returns_400(client):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "3",
    }
    response = c.post("/purchasePlaces", data=data)
    decoded = html.unescape(response.get_data(as_text=True))

    assert response.status_code == 400
    assert "terminée" in decoded

def test_today_competition_is_bookable(client):
    c, clubs, competitions = client
    competitions[0]["date"] = (datetime.now() + timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "1",
    }
    response = c.post("/purchasePlaces", data=data)
    decoded = html.unescape(response.get_data(as_text=True))

    assert response.status_code == 200
    assert "Great-booking complete!" in decoded
