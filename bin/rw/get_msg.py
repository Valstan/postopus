def get_msg(vkapp, group, offset=0, count=1):
    return vkapp.wall.get(owner_id=group, count=count, offset=offset)['items']


if __name__ == '__main__':
    pass
