import requests

from config import tb_url, tb_params, TELEGA_TOKEN_VALSTANBOT


def send_error(session, text):

    method = tb_url + session['TELEGA_TOKEN_VALSTANBOT'] + "/sendMessage"
    tb_params['text'] = str(text) + str(session)

    requests.post(method, data=tb_params)


if __name__ == '__main__':
    sessia = {'TELEGA_TOKEN_VALSTANBOT': TELEGA_TOKEN_VALSTANBOT}
    send_error(sessia, "Запущен файл send_error вручную.")
