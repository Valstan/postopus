from vk_api import VkApi

import config

session = config.session


def del_delete_users(vk, group_id):
    members = vk.groups.getMembers(group_id=group_id)
    count_all = members['count']
    print("Всего подписчиков - ", count_all)
    offset_all = 1000
    members = members['items']
    while offset_all < count_all:
        members.extend(vk.groups.getMembers(
            group_id=group_id, offset=offset_all)['items'])
        offset_all += 1000

    print(f"Получил количество id - {len(members)}")

    persons = []
    offset_all = 0
    while offset_all < count_all:
        mem = ",".join(map(str, members[offset_all:]))
        persons.extend(vk.users.get(user_ids=mem, fields="deactivated,city"))
        offset_all += 1000

    count = 0
    for i in persons:
        count += 1
        if "deactivated" in i:
            print(f"{count} Удаляем {i}")
            vk.groups.removeUser(group_id=group_id, user_id=i['id'])


def clear_banned_list(vk, group_id):
    banned = vk.groups.getBanned(group_id=group_id, fields='deactivated,city', v=5.92)
    count_banned = banned['count']
    print("Всего забаненных в группе - ", count_banned)
    offset_banned = 200
    banned = banned['items']
    while offset_banned < count_banned:
        banned.extend(vk.groups.getBanned(
            group_id=group_id, count=200, offset=offset_banned, fields='deactivated,city', v=5.92)['items'])
        offset_banned += 200
    count = 0
    for i in banned:
        count += 1
        if "profile" not in i:
            print("Не юзер - ", i)
            continue
        if "deactivated" in i:
            print(f"{count} Удаляем {i}")
            vk.groups.unban(group_id=group_id, user_id=i["id"])


def start(name):
    if name == 1:
        token = session["VK_TOKEN_VALSTAN"]
        id_group = 158787639
    else:
        token = session["VK_TOKEN_DRAN"]
        id_group = 187462239

    vk_session = VkApi(token=token)
    vk = vk_session.get_api()

    del_delete_users(vk, id_group)
    clear_banned_list(vk, id_group)


if __name__ == '__main__':
    start(2)  # 1 - МалмыжИнфо, 2 - Драндулет
