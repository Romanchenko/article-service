import os
import json
import urllib
import hashlib
import requests
import streamlit as st
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
        response = requests.get(HOST + "/stats/authors/top/?count=10", headers=headers)
        if response.status_code == 200:
            for auth in response.json()['authors']:
                st.write(auth['name'])






    # progress_bar = st.sidebar.progress(0)
    # status_text = st.sidebar.empty()
    # last_rows = np.random.randn(1, 1)
    # chart = st.line_chart(last_rows)
    #
    # for i in range(1, 101):
    #     new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
    #     status_text.text("%i%% Complete" % i)
    #     chart.add_rows(new_rows)
    #     progress_bar.progress(i)
    #     last_rows = new_rows
    #     time.sleep(0.05)
    #
    # progress_bar.empty()
    #
    # # Streamlit widgets automatically run the script from top to bottom. Since
    # # this button is not connected to any other logic, it just causes a plain
    # # rerun.
    # st.button("Re-run")