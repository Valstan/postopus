import traceback

from bin.utils.send_error import send_error
from config import session


def post_msg(group, text_send, attachments, from_group=1):

    try:
        session['vk_app'].wall.post(owner_id=group,
                                    from_group=from_group,
                                    message=text_send,
                                    attachments=attachments)
    except Exception as exc:
        send_error(__name__, exc, traceback.print_exc())


if __name__ == '__main__':
    pass
