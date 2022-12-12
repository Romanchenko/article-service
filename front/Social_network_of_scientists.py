import streamlit as st
from streamlit_login_auth_ui.widgets import __login__

import requests
import datetime
import json
import os
import urllib
import hashlib
import pandas as pd


HOST = f"http://{os.getenv('WEB_ADDRESS', 'localhost:8002')}"

st.set_page_config(page_title="Social_network_of_scientists", page_icon="👋",)

__login__obj = __login__(auth_token = "courier_auth_token",
                    company_name = "Shims",
                    width = 200, height = 250,
                    logout_button_name = 'Logout', hide_menu_bool = False,
                    hide_footer_bool = False,
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')


def get_login_and_password():
    login = __login__obj.cookies['__streamlit_login_signup_ui_username__']

    def get_password(username):
        with open("_secret_auth_.json", "r") as auth_json:
            authorized_user_data = json.load(auth_json)

        password = 'password'
        for registered_user in authorized_user_data:
            if registered_user['username'] == username:
                password = registered_user[password][-10:]

        return password

    password = get_password(login)

    return login, password


def check_connect():
    content = requests.get(HOST + "/ping")
    st.write('Ping web:', content.status_code)

    return content.status_code == 200


def registration(login, password):
    password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
    data = {"login": login, "password_hash": password_hash}
    requests.post(url=HOST + '/users', json=data)


def authorization(login, password):
    access_token = None

    data = urllib.parse.urlencode({'grant_type': 'password', 'username': login, 'password': password})
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    res = requests.post(url=HOST + '/login', data=data, headers=headers)
    if res.status_code == 200 and 'access_token' in res.json():
        access_token = res.json()['access_token']
    else:
        registration(login, password)
        authorization(login, password)

    return access_token


def add_new_article():
    st.write("### Добавить статью")
    new_article_author = st.text_input('Автор новой статьи', login)
    new_article_title = st.text_input('Название новой статьи')
    new_article_abstract = st.text_input('Описание статьи')
    new_article_link = st.text_input('Ссылка на статью')

    add_article = st.button('Добавить статью')
    if add_article and new_article_title:
        response = requests.post(HOST + "/authors", json={"name": new_article_author}, headers=headers)
        if response.status_code == 200:
            new_authors_id = response.json()['id']

            data = {
                "authors": [new_authors_id],
                "abstract": new_article_abstract,
                "title": new_article_title,
                "url": [new_article_link],
                "year": datetime.datetime.now().year
            }

            response = requests.post(HOST + "/articles", json=data, headers=headers)
            if response.status_code == 200:
                st.write('Статья добавлена')

    elif add_article:
        st.write("Напишите хотя бы как называется ваша статья")


def find_article():
    st.write("### Поиск статей")
    find_article_title = st.text_input('Название статьи')
    full_match_article_title = st.checkbox('Полное совпадение')

    find_article_year = st.text_input('Год публикации статьи')

    find_article_author = st.text_input('Автор статьи')

    if find_article_title:
        title_json = {
            'field': 'title',
            'value': find_article_title,
            'full_match': full_match_article_title
        }
    else:
        title_json = None

    if find_article_year:
        year_json = {
            'field': 'year',
            'value': find_article_year,
            'full_match': True
        }
    else:
        year_json = None

    if find_article_author:
        author_json = {
            'field': 'authors',
            'value': find_article_author,
            'full_match': False
        }
    else:
        author_json = None

    result_json = []
    for i in (title_json, year_json, author_json):
        if i:
            result_json.append(i)

    press_find = st.button('Поиск')
    if press_find and len(result_json) > 0:
        response = requests.get(HOST + '/articles', json=result_json, headers=headers)

        n_articles = len(response.json())


        if n_articles:
            st.write(f'Найдено статей: {n_articles}')
            df = pd.DataFrame(response.json())[['title', 'year', 'authors', 'keywords', 'url', 'tag']]

            def get_name_authors(ids_):
                res = []
                for id_ in ids_:
                    response = requests.get(HOST + '/authors/' + id_, headers=headers)
                    if response.status_code == 200:
                        res.append(response.json()['name'])

                return res

            df.authors = df.authors.apply(lambda x: get_name_authors(x))
            df.columns = ["Название статьи", "Год публикации", "Автор", "Ключевые слова", "Ссылка"]
            st.dataframe(df)
        else:
            st.write(f'Ничего не найдено')

    elif press_find:
        st.write('Заполните любую колонку')


def make_recommendation():
    st.write("### Рекомендации")
    rec_author = st.text_input('Введите автора для кого рекомендовать соавтора и статьи', login)

    if st.button('Рекомендовать соавтора') and rec_author:
        # response = requests.get(HOST + "/stats/authors/top/?count=8", headers=headers)
        author_json = requests.get(HOST + f"/author?name={rec_author}", headers=headers)
        if author_json.status_code != 200:
            st.write(f"Author {rec_author} not found")
        else:
            author_id = author_json.json()["_id"]
            response = requests.get(HOST + f"/stats/authors/rec/?count=10&author_id={author_id}", headers=headers)
            if response.status_code == 200:
                for auth in response.json()['authors']:
                    st.write(auth['name'])

    if st.button('Рекомендовать статьи') and rec_author:
        author_json = requests.get(HOST + f"/author?name={rec_author}", headers=headers)
        if author_json.status_code != 200:
            st.write(f"Author {rec_author} not found")
        else:
            author_id = author_json.json()["_id"]
            response = requests.get(HOST + f"/stats/authors/rec/articles?author_id={author_id}", headers=headers)
            if response.status_code == 200:
                for article in response.json()['articles']:
                    st.write(article['title'])
        st.write("1984")


LOGGED_IN = __login__obj.build_login_ui()

if LOGGED_IN:
    login, password = get_login_and_password()  # из сессии streamlit

    st.write(f"# Welcome to Social network of scientists {login}! 👋")

    if check_connect():
        access_token = authorization(login, password)
        headers = {"Authorization": f"Bearer {access_token}"}

        add_new_article()

        find_article()

        make_recommendation()
