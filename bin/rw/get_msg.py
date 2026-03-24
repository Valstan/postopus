import traceback

from bin.utils.send_error import send_error
from config import session


def get_msg(group, offset=0, count=1):
    """
    Получает посты из группы VK.
    Возвращает пустой список при ошибке (например, invalid access_token).
    """

    try:
        return session['vk_app'].wall.get(owner_id=group, count=count, offset=offset)['items']
    except Exception as exc:
        # Логируем ошибку но не прерываем выполнение
        error_msg = str(exc)
        # Игнорируем ошибки доступа для закрытых групп - это нормально
        if ('invalid access_token' in error_msg or 
            'User authorization failed' in error_msg or
            'Access denied: this wall available only for community members' in error_msg):
            pass
        else:
            send_error(__name__, exc, traceback.print_exc())
        return []  # Возвращаем пустой список вместо None чтобы избежать ошибок в вызывающем коде


if __name__ == '__main__':
    pass
