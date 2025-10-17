import html
import pytest
from server import showSummary
from flask import Flask

def test_show_summary_unknown_email_returns_400(client):
    c, _, _ = client
    response = c.post("/showSummary", data={"email": "invalid@example.com"})
    assert response.status_code == 400
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Sorry, that email wasn't found" in decoded

def test_show_summary_known_email_returns_200(client):
    c, clubs_list, _ = client
    response = c.post("/showSummary", data={"email": clubs_list[0]["email"]})
    assert response.status_code == 200
    decoded = html.unescape(response.get_data(as_text=True))
    assert "Welcome" in decoded
    
    
def test_full_login_flow_with_unknown_email(client):
    c, _, _ = client

    response_index = c.get("/")
    assert response_index.status_code == 200

    response_summary = c.post("/showSummary", data={"email": "notfound@club.com"})
    assert response_summary.status_code == 400
    decoded = html.unescape(response_summary.get_data(as_text=True))
    assert "Sorry, that email wasn't found" in decoded

def test_full_login_flow_with_valid_email(client):
    c, clubs_list, _ = client

    response_index = c.get("/")
    assert response_index.status_code == 200

    response_summary = c.post("/showSummary", data={"email": clubs_list[0]["email"]})
    assert response_summary.status_code == 200
    decoded = html.unescape(response_summary.get_data(as_text=True))
    assert "Welcome" in decoded

def fake_render_template(template_name, **context):
    return f"{template_name} - {context}"

def test_show_summary_returns_400_for_unknown_email(monkeypatch):
    monkeypatch.setattr("server.clubs", [{"name": "Known", "email": "known@test.com"}])
    monkeypatch.setattr("server.competitions", [{"name": "Comp", "date": "2099-01-01 10:00:00"}])
    monkeypatch.setattr("server.render_template", fake_render_template)

    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={"email": "unknown@test.com"}):
        response, status = showSummary()
        assert status == 400
        assert "index.html" in response
        assert "unknown@test.com" not in response

def test_show_summary_returns_200_for_known_email(monkeypatch):
    monkeypatch.setattr("server.clubs", [{"name": "Known", "email": "known@test.com"}])
    monkeypatch.setattr("server.competitions", [{"name": "Comp", "date": "2099-01-01 10:00:00"}])
    monkeypatch.setattr("server.render_template", fake_render_template)

    app = Flask(__name__)
    app.secret_key = "test_secret"

    with app.test_request_context(method="POST", data={"email": "known@test.com"}):
        response = showSummary()
        assert "welcome.html" in response
        assert "Known" in response