import pytest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server import app, loadClubs, loadCompetitions

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_club():
    clubs = loadClubs()
    return clubs[0]

@pytest.fixture
def sample_competition():
    competitions = loadCompetitions()
    return competitions[0]
