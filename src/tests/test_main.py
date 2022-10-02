import hashlib
import json

from starlette.testclient import TestClient
from app.main import app

from app.models.article import Article

client = TestClient(app)


def test_insert_document():
    response = client.post("/articles", json={'title': 'title', 'year': int(2022)})
    assert response.status_code == 200
    doc_id = response.json()['id']
    check_doc = client.get(f"/articles/{doc_id}")
    assert check_doc.status_code == 200
    assert check_doc.json()['title'] == 'title'
    assert check_doc.json()['id'] == doc_id
    assert check_doc.json()['year'] == 2022


def test_no_document():
    doc_id = '6039e21760518101740d5f7b'
    r = client.get(f"/articles/{doc_id}")
    assert r.status_code == 404


def test_delete_document():
    response = client.post("/articles", json={'title': 'title', 'year': int(2022)})
    assert response.status_code == 200
    doc_id = response.json()['id']
    check_doc = client.get(f"/articles/{doc_id}")
    assert check_doc.status_code == 200
    assert check_doc.json()['title'] == 'title'
    assert check_doc.json()['id'] == doc_id
    assert check_doc.json()['year'] == 2022
    delete_doc = client.delete(f"/articles/{doc_id}")
    assert delete_doc.status_code == 200

    r = client.get(f"/articles/{doc_id}")
    assert r.status_code == 404


def test_insert_author():
    response = client.post("/authors", json={'name': 'Ivan Ivanov'})
    assert response.status_code == 200
    author_id = response.json()['id']
    author = client.get(f"/authors/{author_id}")
    assert author.status_code == 200
    assert author.json()['name'] == 'Ivan Ivanov'
    delete_r = client.delete(f"/authors/{author_id}")
    assert delete_r.status_code == 200
    assert client.get(f"/authors/{author_id}").status_code == 404


def test_insert_user():
    response = client.post("/users", json={'login': 'Ivan Ivanov', 'password': 'qwerty1234'})
    assert response.status_code == 200
    user_id = response.json()['id']
    user_response = client.get(f"/users/{user_id}")
    assert user_response.status_code == 200
    assert user_response.json()['login'] == 'Ivan Ivanov'
    assert user_response.json()['password_hash'] == hashlib.md5('qwerty1234'.encode('utf-8')).hexdigest()
    deletion_response = client.delete(f"/users/{user_id}")
    assert deletion_response.status_code == 200
    assert client.get(f"/users/{user_id}").status_code == 404