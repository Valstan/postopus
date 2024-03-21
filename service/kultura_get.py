import time

import requests

from bin.rw.open_file_json import open_file_json
from bin.rw.save_file_json import save_file_json



def read_p(count):
    group_ids_str = ''
    get_posts = []
    batch = 24
    group_list = [
        -179595292,
    ]

    while len(group_list):
        if len(group_list) < batch:
            batch = len(group_list)
        group_ids_str += ','.join(map(str, group_list[:batch])) + ','
        for i in range(3):
            try:
                get_posts.extend(requests.post(
                    f"https://api.vk.com/method/execute.wallGet?groups_id={group_ids_str}&count={count}"
                    f"&access_token=vk1.a.cDaQ017LV8SsLlB3S8g-PgiRPGSIV4HnRzzPCmBhklA4dwa44zh_cZAoXC9tFd3fFu5h3Cg88iQ"
                    f"mwjMjnygkrcv_VI9ybcemSRTzHGvDUAriBLImbV514LKZyPzZ2r9caiwsnft-U4XLzs3vJuX5F1XrXsGUntxI6M5SRPQaGWn"
                    f"DZQpSqhofIJvM2MXtAVr_P1xxihmN5qK-W_orxTsHLw&v=5.131").json()['response'])
                break
            except:
                time.sleep(1)

        group_list = group_list[batch:]

    posts = []
    for i in get_posts:
        posts.extend(i)

    return posts

def kultura():
    base_kultura = open_file_json()

    all_news = read_p(10)

    save_file_json()

if __name__ == '__main__':

    pass
