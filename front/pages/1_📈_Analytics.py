import os
import ast
import json
import urllib
import hashlib

import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go

from wordcloud import WordCloud, STOPWORDS
from streamlit_login_auth_ui.widgets import __login__


HOST = f"http://{os.getenv('WEB_ADDRESS', 'localhost:8002')}"

st.set_page_config(page_title="Analytics", page_icon="📈")

__login__obj = __login__(auth_token = "courier_auth_token",
                    company_name = "Shims",
                    width = 200, height = 250,
                    logout_button_name = 'Logout', hide_menu_bool = False,
                    hide_footer_bool = False,
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN = __login__obj.build_login_ui()


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


if LOGGED_IN == True:
    st.markdown("# Аналитика")

    login, password = get_login_and_password()
    access_token = authorization(login, password)
    headers = {"Authorization": f"Bearer {access_token}"}

    if st.button('Получить топ авторов по цитированию'):
        response = requests.get(HOST + "/stats/authors/top?count=10", headers=headers)
        if response.status_code == 200:
            for auth in response.json()['authors']:
                st.write(auth['name'])


    if st.button('Получить статистику количества статей по годам'):
        df = pd.read_csv('pages/count_for_year.csv', index_col='year')
        fig = px.line(df)
        fig.update_layout(showlegend=False,
                          xaxis_title="Год",
                          yaxis_title="Количество")
        st.plotly_chart(fig, use_container_width=True)


    def plotly_wordcloud(text):
        wc = WordCloud(stopwords=set(STOPWORDS),
                       max_words=200,
                       max_font_size=100)
        wc.generate(text)

        word_list = []
        freq_list = []
        fontsize_list = []
        position_list = []
        orientation_list = []
        color_list = []

        for (word, freq), fontsize, position, orientation, color in wc.layout_:
            word_list.append(word)
            freq_list.append(freq)
            fontsize_list.append(fontsize)
            position_list.append(position)
            orientation_list.append(orientation)
            color_list.append(color)

        x = []
        y = []
        for i in position_list:
            x.append(i[0])
            y.append(i[1])

        new_freq_list = []
        for i in freq_list:
            new_freq_list.append(i * 100)


        trace = go.Scatter(x=x,
                           y=y,
                           textfont=dict(size=new_freq_list,
                                         color=color_list),
                           hoverinfo='text',
                           hovertext=['{0}{1}'.format(w, f) for w, f in zip(word_list, freq_list)],
                           mode='text',
                           text=word_list
                           )

        layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                            'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})

        fig = go.Figure(data=[trace], layout=layout)

        return fig

    years = [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006,2007,
             2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    option = st.selectbox('Выбирите год за который хотите получить статистики по ключевым словам', years)
    if st.button('Получить статистику по ключевым словам'):
        df_keywords = pd.read_csv('pages/keywords.csv')
        tmp = df_keywords[df_keywords.year == option].keywords
        tmp = tmp.dropna()
        tmp = tmp.apply(lambda x: ast.literal_eval(x))
        text = [' '.join(i) for i in tmp]
        text = ' '.join(text)
        st.plotly_chart(plotly_wordcloud(text))
