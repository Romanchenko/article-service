import hashlib
import json
from bson import ObjectId

from starlette.testclient import TestClient
from app.main import app

from app.models.article import Article
from app.storage import articles_storage, authors_storage
from app.storage.articles_storage import find_article_by_field

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