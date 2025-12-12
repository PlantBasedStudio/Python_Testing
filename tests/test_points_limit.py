import html
import pytest
from server import purchasePlaces
from flask import Flask


def test_booking_more_points_than_available_returns_400(client):
    """Test that booking fails when requiring more points than available"""
    c, clubs, competitions = client
    clubs[0]["points"] = "5"
    competitions[0]["numberOfPlaces"] = "20"
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "10"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 400
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Not enough points" in decoded


def test_booking_exactly_available_points_succeeds(client, monkeypatch):
    """Test that booking succeeds when using exactly available points"""
    c, clubs, competitions = client
    clubs[0]["points"] = "10"
    competitions[0]["numberOfPlaces"] = "20"
    
    monkeypatch.setattr("server.saveClubs", lambda x: None)
    monkeypatch.setattr("server.saveCompetitions", lambda x: None)
    
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "10"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 200
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Great-booking complete" in decoded


def test_booking_with_insufficient_points_shows_correct_message(client):
    """Test error message shows current points and required points"""
    c, clubs, competitions = client
    clubs[0]["points"] = "5"
    competitions[0]["numberOfPlaces"] = "20"
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "10"}
    response = c.post("/purchasePlaces", data=data)
    assert response.status_code == 400
    decoded = html.unescape(response.get_data(as_text=True))
    assert "5 points" in decoded
    assert "10" in decoded


def test_points_deducted_after_booking(client, monkeypatch):
    """Test that club points are deducted after successful booking"""
    c, clubs, competitions = client
    initial_points = 15
    places_to_book = 5
    clubs[0]["points"] = str(initial_points)
    competitions[0]["numberOfPlaces"] = "20"
    
    monkeypatch.setattr("server.saveClubs", lambda x: None)
    monkeypatch.setattr("server.saveCompetitions", lambda x: None)
    
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": str(places_to_book)}
    response = c.post("/purchasePlaces", data=data)
    
    assert response.status_code == 200
    assert int(clubs[0]["points"]) == initial_points - places_to_book


def test_full_booking_flow_with_points_deduction(client, monkeypatch):
    """Integration test: full booking flow with points deduction"""
    c, clubs, competitions = client
    clubs[0]["points"] = "15"
    competitions[0]["numberOfPlaces"] = "20"
    
    saved_clubs = []
    def fake_saveClubs(data):
        saved_clubs.append(data)
    
    monkeypatch.setattr("server.saveClubs", fake_saveClubs)
    monkeypatch.setattr("server.saveCompetitions", lambda x: None)
    
    response_summary = c.post("/showSummary", data={"email": clubs[0]["email"]})
    assert response_summary.status_code == 200
    
    data = {"club": clubs[0]["name"], "competition": competitions[0]["name"], "places": "5"}
    response = c.post("/purchasePlaces", data=data)
    
    assert response.status_code == 200
    assert int(clubs[0]["points"]) == 10  # 15 - 5 = 10
    assert len(saved_clubs) > 0


@pytest.fixture
def mock_templates(monkeypatch):
    def fake_render_template(template_name, **context):
        return f"Rendered {template_name} with {context}"
    monkeypatch.setattr("server.render_template", fake_render_template)


def test_purchasePlaces_deducts_points_unit(client, mock_templates):
    """Unit test: purchasePlaces function deducts points correctly"""
    c, clubs, competitions = client
    clubs[0]["points"] = "20"
    competitions[0]["numberOfPlaces"] = "50"
    
    app = Flask(__name__)
    app.secret_key = "test_secret"
    
    with app.test_request_context(method="POST", data={
        "club": clubs[0]["name"], 
        "competition": competitions[0]["name"], 
        "places": "8"
    }):
        purchasePlaces()
        assert int(clubs[0]["points"]) == 12  # 20 - 8 = 12


def test_purchasePlaces_rejects_insufficient_points_unit(client, mock_templates):
    """Unit test: purchasePlaces rejects booking when not enough points"""
    c, clubs, competitions = client
    clubs[0]["points"] = "3"
    competitions[0]["numberOfPlaces"] = "50"
    
    app = Flask(__name__)
    app.secret_key = "test_secret"
    
    with app.test_request_context(method="POST", data={
        "club": clubs[0]["name"], 
        "competition": competitions[0]["name"], 
        "places": "10"
    }):
        response, status = purchasePlaces()
        assert status == 400
        assert "Not enough points" in response
