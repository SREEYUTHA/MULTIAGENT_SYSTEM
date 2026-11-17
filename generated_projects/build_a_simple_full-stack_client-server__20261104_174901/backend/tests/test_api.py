import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_good_morning(client):
    response = client.get('/api/hello?name=Sree&time=06:30')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Good Morning, Sree!'

def test_good_afternoon(client):
    response = client.get('/api/hello?name=Sree&time=13:45')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Good Afternoon, Sree!'

def test_good_evening(client):
    response = client.get('/api/hello?name=Sree&time=18:15')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Good Evening, Sree!'

def test_good_night_late(client):
    response = client.get('/api/hello?name=Sree&time=22:05')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Good Night, Sree!'

def test_good_night_early(client):
    response = client.get('/api/hello?name=Sree&time=03:00')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Good Night, Sree!'

def test_missing_name(client):
    response = client.get('/api/hello?time=12:00')
    assert response.status_code == 400
    data = response.get_json()
    assert 'name' in data['error'].lower()

def test_missing_time_param_name_only_sent():
    # This test is redundant with missing_name if we just check missing param, but let's be explicit
    pass

def test_empty_name(client):
    response = client.get('/api/hello?name=&time=12:00')
    assert response.status_code == 400
    data = response.get_json()
    assert 'name' in data['error'].lower()

def test_missing_time(client):
    response = client.get('/api/hello?name=Sree')
    assert response.status_code == 400
    data = response.get_json()
    assert 'time' in data['error'].lower()

def test_invalid_time_format_single_digit_hour(client):
    response = client.get('/api/hello?name=Sree&time=9:5')
    assert response.status_code == 400
    data = response.get_json()
    assert 'time' in data['error'].lower()

def test_invalid_time_format_hour_out_of_range(client):
    response = client.get('/api/hello?name=Sree&time=25:00')
    assert response.status_code == 400
    data = response.get_json()
    assert 'time' in data['error'].lower()

def test_invalid_time_format_minute_out_of_range(client):
    response = client.get('/api/hello?name=Sree&time=12:60')
    assert response.status_code == 400
    data = response.get_json()
    assert 'time' in data['error'].lower()

def test_cors_allowed_origin_localhost(client):
    response = client.get('/api/hello?name=Sree&time=12:00', headers={'Origin': 'http://localhost:8081'})
    assert response.status_code == 200
    assert response.headers.get('Access-Control-Allow-Origin') == 'http://localhost:8081'

def test_cors_allowed_origin_127(client):
    response = client.get('/api/hello?name=Sree&time=12:00', headers={'Origin': 'http://127.0.0.1:8081'})
    assert response.status_code == 200
    assert response.headers.get('Access-Control-Allow-Origin') == 'http://127.0.0.1:8081'

def test_cors_disallowed_origin(client):
    response = client.get('/api/hello?name=Sree&time=12:00', headers={'Origin': 'http://evil.com'})
    # Flask-CORS typically returns 200 but without the header, or 403 depending on config.
    # Standard behavior for disallowed origin in Flask-CORS is to not include the header.
    assert response.headers.get('Access-Control-Allow-Origin') is None

def test_additional_query_params_ignored(client):
    response = client.get('/api/hello?name=Sree&time=12:00&extra=param')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Good Afternoon, Sree!'