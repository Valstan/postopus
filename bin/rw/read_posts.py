import time

import requests

from config import session


def read_posts(group_dict, count):
    group_ids_str = ''
    get_posts = []
    batch = 24
    group_list = list(group_dict.values())

    while len(group_list):
        if len(group_list) < batch:
            batch = len(group_list)
        group_ids_str += ','.join(map(str, group_list[:batch])) + ','
        for i in range(3):
            try:
                get_posts.extend(requests.post(
                    f"https://api.vk.com/method/execute.wallGet?groups_id={group_ids_str}&count={count}"
                    f"&access_token={session['token']}&v=5.131").json()['response'])
                break
            except:
                time.sleep(1)

        group_list = group_list[batch:]

    posts = []
    for i in get_posts:
        posts.extend(i)

    return posts


if __name__ == '__main__':
    pass
