import streamlit as st
from streamlit_login_auth_ui.widgets import __login__

import requests
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
    print(len(result_json))
    if st.button('Поиск') and len(result_json) > 0:
        response = requests.get(host + '/articles', json=result_json, headers=headers)
        st.write(f'Найдено статей: {len(response.json())}')
        df = pd.DataFrame(response.json())[['title', 'year', 'authors', 'keywords']]

        def get_name_authors(ids_):
            res = []
            for id_ in ids_:
                response = requests.get(host + '/authors/' + id_, headers=headers)
                if response.status_code == 200:
                    res.append(response.json()['name'])

            return res

        df.authors = df.authors.apply(lambda x: get_name_authors(x))
        df.columns = ["Название статьи", "Год публикации", "Автор", "Ключивые слова"]
        st.dataframe(df)




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