import requests

from se_config import TELEGA_API_TOKEN, URL, parametrs


def send_error(text):
    method = URL + TELEGA_API_TOKEN + "/sendMessage"
    parametrs['text'] = str(text)

    requests.post(method, data=parametrs)


if __name__ == '__main__':
    send_error("Запущен файл send_error вручную.")
