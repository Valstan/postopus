import traceback

from bin.rw.get_session_vk_api import get_session_vk_api
from bin.utils.send_error import send_error
from config import session


def post_msg(group, text_send, attachments='', from_group=1, copy_right=''):

    if session['name_base'] in 'mi' and session['VK_TOKEN_VALSTAN'] not in session['token']:
        session.update({"token": session['VK_TOKEN_VALSTAN']})
        get_session_vk_api()

    try:
        session['vk_app'].wall.post(owner_id=group,
                                    from_group=from_group,
                                    message=text_send,
                                    attachments=attachments,
                                    copyright=copy_right)
    except Exception as exc:
        send_error(__name__, exc, traceback.print_exc())


if __name__ == '__main__':
    pass
