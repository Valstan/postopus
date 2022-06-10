import os

import requests


def send_error(text):
    tb_url = 'https://api.telegram.org/bot'
    tb_params = {'chat_id': -1001746966097}  # канал Тест-тест-тест2000
    method = tb_url + os.getenv('TELEGA_TOKEN_VALSTANBOT') + "/sendMessage"
    tb_params['text'] = str(text)

    requests.post(method, data=tb_params)


if __name__ == '__main__':
    send_error("Запущен файл send_error вручную.")
