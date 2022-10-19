import streamlit as st
from streamlit_login_auth_ui.widgets import __login__

import requests
import json


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
    # st.sidebar.success("Select a demo above.")

    import os
    import urllib
    import hashlib


    web_address = os.getenv('WEB_ADDRESS', 'localhost:8002')
    host = f"http://{web_address}"

    content = requests.get(host + "/ping")
    st.write('Ping db:', content.status_code)

    login = "str1"
    password = 'str1'

    # registragion
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

    # add articles
    article_title = st.text_input('Название для вашей статьи', 'Новая статья')
    res = requests.post(host + '/articles', headers=headers, json={"title": article_title, "year": 0})
    res.json()
    st.write(res.json())

    title = st.text_input('Поиск заголовка по ID', '634db1544366c9b97ff94d02')
    content = requests.get(host + "/articles/" + title, headers=headers)
    print(content.status_code)
    if content.status_code == 200:
        st.write('Заголовок найденной статьи:', json.loads(content.content)['title'])
    else:
        st.write('Статья не найденна:', title)


    # number = st.number_input('Insert a number')
    # st.write('The current number is ', number)
    # print(number)
