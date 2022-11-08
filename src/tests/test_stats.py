from .test_main import setup, TestData, post, get


def test_get_top(setup):
    response = post("/authors", json={'name': 'Ivan Ivanov'}, setup=setup)
    id1 = response.json()['id']
    response = post("/authors", json={'name': 'Ivan Smirnov'}, setup=setup)
    id2 = response.json()['id']
    response = post("/authors", json={'name': 'Nikolay Tikhonov'}, setup=setup)
    id3 = response.json()['id']

    response = post("/articles", json={
        'title': 'title',
        'year': int(2022),
        'authors': [id1],
        'references': [],
        'keywords': ['pepa']
    }, setup=setup)
    article_id_1 = response.json()['id']

    response = post("/articles", json={
        'title': 'title',
        'year': int(2022),
        'authors': [id1, id2],
        'references': []
    }, setup=setup)
    article_id_2 = response.json()['id']

    response = post("/articles", json={
        'title': 'title',
        'year': int(2022),
        'authors': [id1, id3],
        'references': [],
        'keywords': ['pepa']
    }, setup=setup)
    article_id_3 = response.json()['id']

    response = post("/articles", json={
        'title': 'title',
        'year': int(2022),
        'authors': [],
        'references': [article_id_1, article_id_3, article_id_2]
    }, setup=setup)
    sz = 2

    top_authors = get(f"/stats/authors/top?count={sz}", setup)
    assert len(top_authors.json()['authors']) == 2
    authors = top_authors.json()['authors']
    assert authors[0]['_id'] == id1
    assert authors[0]['name'] == 'Ivan Ivanov'
    assert authors[1]['_id'] == id2
    assert authors[1]['name'] == 'Ivan Smirnov'


# def test_top_by_keyword(setup):
#     response = post("/authors", json={'name': 'Ivan Ivanov'}, setup=setup)
#     id1 = response.json()['id']
#     response = post("/authors", json={'name': 'Ivan Smirnov'}, setup=setup)
#     id2 = response.json()['id']
#     response = post("/authors", json={'name': 'Nikolay Tikhonov'}, setup=setup)
#     id3 = response.json()['id']
#
#     response = post("/articles", json={
#         'title': 'title',
#         'year': int(2022),
#         'authors': [id1],
#         'references': [],
#         'keywords': ['pepa']
#     }, setup=setup)
#     article_id_1 = response.json()['id']
#
#     response = post("/articles", json={
#         'title': 'title',
#         'year': int(2022),
#         'authors': [id1, id2],
#         'references': []
#     }, setup=setup)
#     article_id_2 = response.json()['id']
#
#     response = post("/articles", json={
#         'title': 'title',
#         'year': int(2022),
#         'authors': [id1, id3],
#         'references': [],
#         'keywords': ['pepa']
#     }, setup=setup)
#     article_id_3 = response.json()['id']
#
#     response = post("/articles", json={
#         'title': 'title',
#         'year': int(2022),
#         'authors': [id1, id2],
#         'references': []
#     }, setup=setup)
#     article_id_4 = response.json()['id']
#
#     response = post("/articles", json={
#         'title': 'title',
#         'year': int(2022),
#         'authors': [],
#         'references': [article_id_1, article_id_3, article_id_2]
#     }, setup=setup)
#     sz = 2
#
#     top_authors = get(f"/stats/authors/top?count={sz}&keyword=pepa", setup)
#     assert len(top_authors.json()['authors']) == 2
#     authors = top_authors.json()['authors']
#     assert authors[0]['_id'] == id1
#     assert authors[0]['name'] == 'Ivan Ivanov'
#     assert authors[1]['_id'] == id3
#     assert authors[1]['name'] == 'Nikolay Tikhonov'
#

