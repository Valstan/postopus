import traceback

from bin.utils.send_error import send_error
from env_loader import session

def post_msg(group, text_send, attachments='', from_group=1, copy_right=''):
    """
    Публикует пост ВКонтакте.
    
    Args:
        group: ID группы для публикации
        text_send: Текст поста
        attachments: Вложения (фото, видео и т.д.)
        from_group: Публиковать от имени группы (1) или пользователя (0)
        copy_right: Копирайт (ссылка на источник)
    
    Returns:
        dict с информацией о посте {'post_id': ..., 'url': ...} или None при ошибке
    """
    try:
        response = session['vk_app'].wall.post(
            owner_id=group,
            from_group=from_group,
            message=text_send,
            attachments=attachments,
            copyright=copy_right
        )
        
        # Возвращаем информацию о созданном посте
        if response and 'post_id' in response:
            post_id = response['post_id']
            post_url = f"https://vk.com/wall{group}_{post_id}"
            return {
                'post_id': post_id,
                'url': post_url,
                'owner_id': group
            }
        return None
        
    except Exception as exc:
        send_error(__name__, exc, traceback.print_exc())
        return None


if __name__ == '__main__':
    pass
