from time import sleep

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.storage.mongo_client import client as db_client

client = TestClient(app)


@pytest.fixture
def setup():
    db_client.drop_database(name_or_database='main')
    yield ""
    db_client.drop_database(name_or_database='main')


def test_login(setup):
    password = 'qwerty123'
    login = 'chuppy'
    response = client.post("/users", json={'login': login, 'password': password})
    assert response.status_code == 200

    # we can't login without token
    response = client.post("/articles", json={'title': 'title', 'year': int(2022)})
    assert response.status_code == 401

    response = client.post("/login", data={'username': login, 'password': password, 'grant_type': 'password'})
    assert response.status_code == 200
    token = response.json()['access_token']
    assert response.json()['token_type'] == 'bearer'

    response = client.post("/articles", json={'title': 'title', 'year': int(2022)},
                           headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200


def test_login_for_unknown_user(setup):
    response = client.post("/login",
                           data={'username': 'unknown_login', 'password': 'password', 'grant_type': 'password'})
    assert response.status_code == 401


def test_login_expiration(setup):
    password = 'qwerty123'
    login = 'chuppy'
    response = client.post("/users", json={'login': login, 'password': password})
    assert response.status_code == 200
    response = client.post("/login", data={'username': login, 'password': password, 'grant_type': 'password'})
    assert response.status_code == 200
    token = response.json()['access_token']

    sleep(4)

    response = client.post("/articles", json={'title': 'title', 'year': int(2022)},
                           headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401
    response = client.post("/login", data={'username': login, 'password': password, 'grant_type': 'password'})
    assert response.status_code == 200
    token = response.json()['access_token']
    response = client.post("/articles", json={'title': 'title', 'year': int(2022)},
                           headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
