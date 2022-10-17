import hashlib
import json

from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login():
    password = 'qwerty123'
    login = 'chuppy'
    response = client.post("/users", json={'login': login, 'password': password})
    assert response.status_code == 200

    # we can't login without token
    response = client.post("/articles", json={'title': 'title', 'year': int(2022)})
    assert response.status_code == 401

    response = client.post("/login?", data={'username': login, 'password': password, 'grant_type': 'password'})
    assert response.status_code == 200
    token = response.json()['access_token']
    assert response.json()['token_type'] == 'bearer'

    response = client.post("/articles", json={'title': 'title', 'year': int(2022)}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200

