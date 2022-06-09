import os

import requests

from config import TB_url, TB_parametrs


def send_error(text):
    method = TB_url + os.getenv('TELEGA_TOKEN_VALSTANBOT') + "/sendMessage"
    TB_parametrs['text'] = str(text)

    requests.post(method, data=TB_parametrs)


if __name__ == '__main__':
    send_error("Запущен файл send_error вручную.")
