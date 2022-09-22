import requests

from config import tb_url, tb_params, session


def send_error(modul_name='?', exception='?', traceback='?'):
    method = tb_url + session['TELEGA_TOKEN_VALSTANBOT'] + "/sendMessage"

    tb_params['text'] = f'МОДУЛЬ:\n{modul_name}\nАШИПКА:\n{exception}\nПРИЧИНА:\n{traceback}\nСЕССИЯ:\n' + str(session)

    requests.post(method, data=tb_params)


if __name__ == '__main__':
    send_error("Запущен файл send_error вручную.")
