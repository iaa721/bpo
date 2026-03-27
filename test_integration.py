import pytest
from app import app
import json

# Не забудьте, что перед запуском тестов нужно подготовить тестовую базу.
# Она должна быть настроена так, чтобы ваши вызовы реальных функций db работали.

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_register_success(client):
    response = client.post('/register', json={'username': 'testuser', 'password': 'pass'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data and data['message'] == 'Registration successful'

def test_login_success(client):
    response = client.post('/login', json={'username': 'testuser', 'password': 'pass'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data

def test_get_games_list(client):
    response = client.get('/games')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_get_game_info_found(client):
    id = "0ed7fc5a-d495-4f62-bf78-17a64ec66a26"
    response = client.get('/games/' + id)
    assert response.status_code == 200
    data = response.get_json()
    assert id in data[0]

def test_get_game_info_not_found(client):
    # замените на несуществующий id
    response = client.get('/games/nonexistent_id')
    assert response.status_code == 404

def test_create_game_success(client):
    token_response = client.post('/login', json={'username': 'testuser', 'password': 'pass'})
    token = token_response.get_json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/games/new', headers=headers, json={'title': 'New Game', 'description': 'Desc'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'game_id' in data

def test_upload_game_success(client):
    token_response = client.post('/login', json={'username': 'testuser', 'password': 'pass'})
    token = token_response.get_json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/games/existing_game_id/upload', headers=headers, json={'download_url': 'http://example.com/game.zip'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Game uploaded'
