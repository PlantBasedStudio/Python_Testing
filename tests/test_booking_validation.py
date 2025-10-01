import pytest

def test_cannot_book_more_places_than_available(client, sample_club, sample_competition):
    """Test que les clubs ne peuvent pas réserver plus de places que disponibles"""
    available_places = int(sample_competition['numberOfPlaces'])
    places_to_book = available_places + 5
    
    response = client.post('/purchasePlaces', data={
        'competition': sample_competition['name'],
        'club': sample_club['name'],
        'places': str(places_to_book)
    })
    
    assert response.status_code == 200
    assert b'Error' in response.data
    assert b'Only' in response.data
    assert b'places available' in response.data


def test_successful_booking_within_limit(client, sample_club, sample_competition):
    """Test qu'une réservation normale fonctionne correctement"""
    places_to_book = 5
    
    response = client.post('/purchasePlaces', data={
        'competition': sample_competition['name'],
        'club': sample_club['name'],
        'places': str(places_to_book)
    })
    
    assert response.status_code == 200
    assert b'Great-booking complete!' in response.data


def test_cannot_book_zero_places(client, sample_club, sample_competition):
    """Test qu'on ne peut pas réserver 0 place"""
    response = client.post('/purchasePlaces', data={
        'competition': sample_competition['name'],
        'club': sample_club['name'],
        'places': '0'
    })
    
    assert response.status_code == 200
    assert b'Error' in response.data
    assert b'greater than 0' in response.data


def test_cannot_book_negative_places(client, sample_club, sample_competition):
    """Test qu'on ne peut pas réserver un nombre négatif de places"""
    response = client.post('/purchasePlaces', data={
        'competition': sample_competition['name'],
        'club': sample_club['name'],
        'places': '-5'
    })
    
    assert response.status_code == 200
    assert b'Error' in response.data
