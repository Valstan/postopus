import requests

from env_loader import logger, session, tb_params, tb_url


def send_error(modul_name="?", exception="?", traceback="?"):
    """
    Отправляет уведомление об ошибке в Telegram.
    НЕRaises исключений при недоступности Telegram!
    """
    try:
        method = tb_url + session.get("TELEGA_TOKEN_VALSTANBOT", "") + "/sendMessage"

        tb_params["text"] = f"МОДУЛЬ:\n{modul_name}\nАШИПКА:\n{exception}\nПРИЧИНА:\n{traceback}\nСЕССИЯ:\n" + str(session)

        response = requests.post(method, data=tb_params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.warning(f"send_error: timeout при отправке ошибки в Telegram")
    except requests.exceptions.ConnectionError as e:
        logger.warning(f"send_error: нет соединения с Telegram ({e})")
    except Exception as e:
        logger.warning(f"send_error: не удалось отправить ошибку в Telegram: {e}")


if __name__ == "__main__":
    send_error("Запущен файл send_error вручную.")
