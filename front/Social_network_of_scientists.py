import streamlit as st
from streamlit_login_auth_ui.widgets import __login__
import streamlit_login_auth_ui

import requests
import datetime
import json
import os
import urllib
import hashlib
import pandas as pd


st.set_page_config(page_title="Social_network_of_scientists", page_icon="👋",)

__login__obj = __login__(auth_token = "courier_auth_token",
                    company_name = "Shims",
                    width = 200, height = 250,
                    logout_button_name = 'Logout', hide_menu_bool = False,
                    hide_footer_bool = False,
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN = __login__obj.build_login_ui()

if LOGGED_IN == True:
    st.write("# Welcome to Social network of scientists! 👋")

    web_address = os.getenv('WEB_ADDRESS', 'localhost:8002')
    host = f"http://{web_address}"

    content = requests.get(host + "/ping")
    st.write('Ping web:', content.status_code)

    # registragion
    login = "str1"
    password = 'str1'
    password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
    data = {"login": login, "password_hash": password_hash}
    requests.post(url=host + '/users', json=data)

    # Authorization
    data = urllib.parse.urlencode({'grant_type': 'password', 'username': login, 'password': password})
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    res = requests.post(url=host + '/login', data=data, headers=headers)
    if 'access_token' in res.json():
        access_token = res.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    # Добавить статью
    st.write("### Добавить статью")
    new_article_author = st.text_input('Автор новой статьи')
    new_article_title = st.text_input('Название новой статьи')
    new_article_abstract = st.text_input('Описание статьи')
    new_article_link = st.text_input('Ссылка на статью')

    add_article = st.button('Добавить статью')
    if add_article and new_article_title:
        response = requests.post(host + "/authors", json={"name": new_article_author}, headers=headers)
        if response.status_code == 200:
            new_authors_id = response.json()['id']

            data = {
                "authors": [new_authors_id],
                "abstract": new_article_abstract,
                "title": new_article_title,
                "url": [new_article_link],
                "year": datetime.datetime.now().year
            }

            response = requests.post(host + "/articles", json=data, headers=headers)
            if response.status_code == 200:
                st.write('Статья добавлена')

    elif add_article:
        st.write("Напишите хотя бы как называется ваша статья")

    # Поиск статей
    st.write("### Поиск статей")
    find_article_title = st.text_input('Название статьи')
    full_match_article_title = st.checkbox('Полное совпадение')

    find_article_year = st.text_input('Год публикации статьи')

    find_article_author = st.text_input('Автор статьи')
    # full_match_article_authors = st.checkbox('Полное совпадение')

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
        response = requests.get(host + '/articles', json=result_json, headers=headers)

        n_articles = len(response.json())


        if n_articles:
            st.write(f'Найдено статей: {n_articles}')
            df = pd.DataFrame(response.json())[['title', 'year', 'authors', 'keywords', 'url']]

            def get_name_authors(ids_):
                res = []
                for id_ in ids_:
                    response = requests.get(host + '/authors/' + id_, headers=headers)
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

    # Рекомендации
    st.write("### Рекомендации")
    rec_author = st.text_input('Введите автора для кого рекомендовать соавтора и статьи', 'John Gold')

    if st.button('Рекомендовать соавтора') and rec_author:
        st.write("Лев Толстой")

    if st.button('Рекомендовать статьи') and rec_author:
        st.write("Война и мир")


    # add articles
    # article_title = st.text_input('Название для вашей статьи', 'Новая статья')
    # res = requests.post(host + '/articles', headers=headers, json={"title": article_title, "year": 0})
    # res.json()
    # st.write(res.json())
    #
    # title = st.text_input('Поиск заголовка по ID', '634db1544366c9b97ff94d02')
    # content = requests.get(host + "/articles/" + title, headers=headers)
    # print(content.status_code)
    # if content.status_code == 200:
    #     st.write('Заголовок найденной статьи:', json.loads(content.content)['title'])
    # else:
    #     st.write('Статья не найденна:', title)


    # number = st.number_input('Insert a number')
    # st.write('The current number is ', number)
    # print(number)