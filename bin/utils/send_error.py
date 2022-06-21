import requests

from config import tb_url, tb_params, session


def send_error(text):
    method = tb_url + session['TELEGA_TOKEN_VALSTANBOT'] + "/sendMessage"
    tb_params['text'] = str(text) + str(session)

    requests.post(method, data=tb_params)


if __name__ == '__main__':
    send_error("Запущен файл send_error вручную.")
