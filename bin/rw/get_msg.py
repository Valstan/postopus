import traceback

from bin.utils.send_error import send_error


def get_msg(session, vk_app, group, offset=0, count=1):
    try:
        return vk_app.wall.get(owner_id=group, count=count, offset=offset)['items']
    except Exception as exc:
        send_error(session,
                   f'Модуль - {get_msg.__name__}\n'
                   f'АШИПКА - {exc}\n'
                   f'{traceback.print_exc()}')
    quit()


if __name__ == '__main__':
    pass
