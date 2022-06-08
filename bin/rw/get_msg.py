def get_msg(vk_app, group, offset=0, count=1):
    return vk_app.wall.get(owner_id=group, count=count, offset=offset)['items']


if __name__ == '__main__':
    pass
