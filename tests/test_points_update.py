from server import app, saveClubs, saveCompetitions
import json
import pytest
import io


def test_purchasePlaces_calls_save_functions(client, monkeypatch):
    c, clubs, competitions = client
    called = {"clubs": False, "competitions": False}

    def fake_saveClubs(_):
        called["clubs"] = True

    def fake_saveCompetitions(_):
        called["competitions"] = True

    monkeypatch.setattr("server.saveClubs", fake_saveClubs)
    monkeypatch.setattr("server.saveCompetitions", fake_saveCompetitions)

    response = c.post("/purchasePlaces", data={
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "3"
    })

    assert response.status_code == 200
    assert b"Great-booking complete" in response.data
    assert called["clubs"]
    assert called["competitions"]
    
    
def test_full_booking_flow_with_save(monkeypatch, client):
    c, clubs, competitions = client
    saved_data = {}

    def fake_saveClubs(data):
        saved_data["clubs"] = data

    def fake_saveCompetitions(data):
        saved_data["competitions"] = data

    monkeypatch.setattr("server.saveClubs", fake_saveClubs)
    monkeypatch.setattr("server.saveCompetitions", fake_saveCompetitions)

    original_places = int(competitions[0]["numberOfPlaces"])

    response = c.post("/purchasePlaces", data={
        "club": clubs[0]["name"],
        "competition": competitions[0]["name"],
        "places": "5"
    })

    assert response.status_code == 200
    assert b"Great-booking complete" in response.data

    assert int(competitions[0]["numberOfPlaces"]) == original_places - 5

    assert "clubs" in saved_data
    assert "competitions" in saved_data
    assert saved_data["competitions"][0]["numberOfPlaces"] == original_places - 5
        
class NonClosingStringIO(io.StringIO):
    def close(self):
        pass 

def test_saveClubs_writes_correct_json(monkeypatch):
    clubs = [{"name": "Test Club", "email": "test@club.com", "points": "10"}]
    buffer = NonClosingStringIO()

    def fake_open(file, mode='r', encoding=None):
        assert file == 'clubs.json'
        assert mode == 'w'
        return buffer

    monkeypatch.setattr("builtins.open", fake_open)

    saveClubs(clubs)
    buffer.seek(0)
    data = json.loads(buffer.getvalue())
    assert "clubs" in data
    assert data["clubs"][0]["name"] == "Test Club"

def test_saveCompetitions_writes_correct_json(monkeypatch):
    competitions = [{"name": "Test Comp", "numberOfPlaces": "20"}]
    buffer = NonClosingStringIO()

    def fake_open(file, mode='r', encoding=None):
        assert file == 'competitions.json'
        assert mode == 'w'
        return buffer

    monkeypatch.setattr("builtins.open", fake_open)

    saveCompetitions(competitions)
    buffer.seek(0)
    data = json.loads(buffer.getvalue())
    assert "competitions" in data
    assert data["competitions"][0]["numberOfPlaces"] == "20"