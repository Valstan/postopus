import traceback

from bin.utils.send_error import send_error


def post_msg(session, vk_app, group, text_send, attachments):
    try:
        vk_app.wall.post(owner_id=group,
                         from_group=1,
                         message=text_send,
                         attachments=attachments)
    except Exception as exc:
        send_error(session,
                   f'Модуль - {post_msg.__name__}\n'
                   f'АШИПКА - {exc}\n'
                   f'{traceback.print_exc()}')
        quit()


if __name__ == '__main__':
    pass
