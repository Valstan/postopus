import os

import requests

from config import tb_url, tb_params


def send_error(text):

    method = tb_url + os.getenv('TELEGA_TOKEN_VALSTANBOT') + "/sendMessage"
    tb_params['text'] = str(text)

    requests.post(method, data=tb_params)


if __name__ == '__main__':
    send_error("Запущен файл send_error вручную.")
