import hashlib

import json
from bson import ObjectId
from dataclasses import dataclass


import pytest
from starlette.testclient import TestClient
from app.main import app

from app.models.article import Article

from app.storage import articles_storage, authors_storage
from app.storage.articles_storage import find_article_by_field
from app.storage.mongo_client import client as db_client


client = TestClient(app)

AUTHORIZATION = 'Authorization'


@dataclass
class TestData:
    login: str
    password: str
    token: str
    auth_header: str


def post(path, json, setup):
    return client.post(path, json=json, headers={AUTHORIZATION: setup.auth_header})


def get(path, setup):
    return client.get(path, headers={AUTHORIZATION: setup.auth_header})


def delete(path, setup):
    return client.delete(path, headers={AUTHORIZATION: setup.auth_header})


@pytest.fixture
def setup():
    db_client.drop_database(name_or_database='main')
    login = 'test_login'
    password = 'qerty123'
    user_response = client.post("/users", json={'login': login, 'password': password})
    token = client.post("/login?", data={'username': login, 'password': password, 'grant_type': 'password'}).json()[
        'access_token']
    yield TestData(login=login, password=password, token=token, auth_header=f'Bearer {token}')
    db_client.drop_database(name_or_database='main')


def test_insert_document(setup):
    response = post("/articles", json={'title': 'title', 'year': int(2022)}, setup=setup)
    assert response.status_code == 200
    doc_id = response.json()['id']
    check_doc = get(f"/articles/{doc_id}", setup)
    assert check_doc.status_code == 200
    assert check_doc.json()['title'] == 'title'
    assert check_doc.json()['id'] == doc_id
    assert check_doc.json()['year'] == 2022


def test_no_document(setup):
    doc_id = '6039e21760518101740d5f7b'
    r = get(f"/articles/{doc_id}", setup)
    assert r.status_code == 404


def test_delete_document(setup):
    response = post("/articles", json={'title': 'title', 'year': int(2022)}, setup=setup)
    assert response.status_code == 200
    doc_id = response.json()['id']
    check_doc = get(f"/articles/{doc_id}", setup)
    assert check_doc.status_code == 200
    assert check_doc.json()['title'] == 'title'
    assert check_doc.json()['id'] == doc_id
    assert check_doc.json()['year'] == 2022
    delete_doc = delete(f"/articles/{doc_id}", setup=setup)
    assert delete_doc.status_code == 200

    r = get(f"/articles/{doc_id}", setup)
    assert r.status_code == 404



def test_search_by_field():
    articles_storage.drop_database()
    authors_storage.drop_database()

    response = client.post("/authors", json={'name': 'Ivan Ivanov'})
    assert response.status_code == 200
    ivan_id = response.json()['id']

    response = client.post("/authors", json={'name': 'John Cena'})
    assert response.status_code == 200
    john_id = response.json()['id']

    response = client.post("/articles", json={'title': 'B', 'year': int(2022)})
    assert response.status_code == 200
    response = client.post("/articles", json={'title': 'A', 'year': int(2022)})
    assert response.status_code == 200
    response = client.post("/articles", json={'title': 'A', 'year': int(2022), 'authors': [john_id, ivan_id]})
    assert response.status_code == 200
    response = client.post("/articles", json={'title': 'Aa', 'year': int(2021), 'authors': [john_id], 'keywords': ['math']})
    assert response.status_code == 200
    response = client.post("/articles", json={'title': 'A B', 'year': int(2022), 'keywords': ['math', 'computer science']})
    assert response.status_code == 200
    response = client.post("/articles", json={'title': 'A A', 'year': int(2021), 'authors': [ivan_id], 'keywords': ['computer science']})
    assert response.status_code == 200

    response = client.get('/articles', json=[
        {
            'field': 'title',
            'value': 'A',
            'full_match': True
        }
    ])
    assert {article['title'] for article in response.json()} == {'A'}

    response = client.get('/articles', json=[
        {
            'field': 'title',
            'value': 'A',
            'full_match': False
        }
    ])
    assert {article['title'] for article in response.json()} == {'A', 'Aa', 'A B', 'A A'}

    response = client.get('/articles', json=[
        {
            'field': 'title',
            'value': 'A',
            'full_match': False
        },
        {
            'field': 'year',
            'value': 2022,
            'full_match': True
        },
    ])
    assert {article['title'] for article in response.json()} == {'A', 'A B'}

    response = client.get('/articles', json=[
        {
            'field': 'authors',
            'value': 'john',
            'full_match': False
        },
    ])
    assert {article['title'] for article in response.json()} == {'A', 'Aa'}

    response = client.get('/articles', json=[
        {
            'field': 'keywords',
            'value': 'math',
            'full_match': True
        },
        {
            'field': 'keywords',
            'value': 'computer',
            'full_match': False
        },
    ])
    assert {article['title'] for article in response.json()} == {'A B'}



def test_insert_author(setup):
    response = post("/authors", json={'name': 'Ivan Ivanov'}, setup=setup)
    assert response.status_code == 200
    author_id = response.json()['id']
    author = get(f"/authors/{author_id}", setup)
    assert author.status_code == 200
    assert author.json()['name'] == 'Ivan Ivanov'
    delete_r = delete(f"/authors/{author_id}", setup)
    assert delete_r.status_code == 200
    assert get(f"/authors/{author_id}", setup).status_code == 404


def test_insert_user(setup):
    response = post("/users", json={'login': 'Ivan Ivanov', 'password': 'qwerty1234'}, setup=setup)
    assert response.status_code == 200
    user_id = response.json()['id']
    user_response = get(f"/users/{user_id}", setup)
    assert user_response.status_code == 200
    assert user_response.json()['login'] == 'Ivan Ivanov'
    assert user_response.json()['password_hash'] == hashlib.md5('qwerty1234'.encode('utf-8')).hexdigest()
    deletion_response = delete(f"/users/{user_id}", setup=setup)
    assert deletion_response.status_code == 200
    assert get(f"/users/{user_id}", setup).status_code == 404
