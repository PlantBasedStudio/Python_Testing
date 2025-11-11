import html
import pytest
from server import clubs_list, clubs, competitions

def test_club_list_page(client):
    c, clubs, competitions = client
    response = c.get("/clubs")
    
    assert response.status_code == 200
    
    html_content = response.get_data(as_text=True)
    
    for club in clubs:
        assert club["name"] in html_content
    
    for comp in competitions:
        assert comp["name"] in html_content
        

def test_club_list_integration_flow(client):
    c, clubs, competitions = client
    
    login_response = c.post("/showSummary", data={"email": clubs[0]["email"]})
    assert login_response.status_code == 200
    
    list_response = c.get("/clubs")
    assert list_response.status_code == 200
    
    html_content = list_response.get_data(as_text=True)
    
    for club in clubs:
        assert club["name"] in html_content
        assert str(club["points"]) in html_content
    
    for comp in competitions:
        assert comp["name"] in html_content
        
def fake_render_template(template_name, **context):
    return {"template": template_name, "context": context}

def test_club_list_unit(monkeypatch):
    monkeypatch.setattr("server.render_template", fake_render_template)
    
    response = clubs_list()
    
    assert response["template"] == "/clubs.html"
    assert response["context"]["clubs"] == clubs
    assert response["context"]["competitions"] == competitions