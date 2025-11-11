import html
import pytest
from server import purchasePlaces
from flask import Flask


def test_booking_more_than_12_places_returns_400(client):
    c, clubs, competitions = client
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "13"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 400
    decoded = html.unescape(response.get_data(as_text=True))
    assert "12 seats" in decoded


def test_booking_12_places_ok(client):
    c, clubs, competitions = client
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "12"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 200
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Great-booking" in decoded or "welcome" in decoded
    
    
def test_full_booking_flow_with_valid_email_and_valid_places(client):
    c, clubs, competitions = client

    response_summary = c.post("/showSummary", data={"email": clubs[0]["email"]})
    assert response_summary.status_code == 200

    response_booking = c.post("/purchasePlaces", data={"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "10"})
    assert response_booking.status_code == 200
    decoded = html.unescape(response_booking.get_data(as_text=True))
    assert "Great-booking" in decoded or "welcome" in decoded


def test_full_booking_flow_more_than_12_places_fails(client):
    c, clubs, competitions = client

    c.post("/showSummary", data={"email": clubs[0]["email"]})
    response_booking = c.post("/purchasePlaces", data={"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "13"})
    assert response_booking.status_code == 400
    decoded = html.unescape(response_booking.get_data(as_text=True))
    assert "12 seats" in decoded


@pytest.fixture
def mock_templates(monkeypatch):
    def fake_render_template(template_name, **context):
        return f"Rendered {template_name} with {context}"
    monkeypatch.setattr("server.render_template", fake_render_template)


def test_purchasePlaces_more_than_12_returns_400(client, mock_templates):
    c, clubs, competitions = client
    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "13"}):
        response, status = purchasePlaces()
        assert status == 400
        assert "12 seats" in response


def test_purchasePlaces_valid_booking(client, mock_templates):
    c, clubs, competitions = client
    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "8"}):
        response = purchasePlaces()
        assert "welcome.html" in response
        assert int(competitions[0]["numberOfPlaces"]) == 12


def test_purchasePlaces_already_booked_too_many(client, mock_templates):
    c, clubs, competitions = client
    clubs[0][competitions[0]["name"]] = 11

    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "3"}):
        response, status = purchasePlaces()
        assert status == 400
        assert "12 seats" in response