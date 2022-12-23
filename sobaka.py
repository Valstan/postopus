from vk_api import VkApi

import config


def del_delete_users():
    members = vk.groups.getMembers(group_id=158787639)
    count_all = members['count']
    print("Всего подписчиков - ", count_all)
    offset_all = 1000
    members = members['items']
    while offset_all < count_all:
        members.extend(vk.groups.getMembers(group_id=158787639, count=1000, offset=offset_all)['items'])
        offset_all += 1000
    count = 0
    for i in members:
        status = vk.users.get(user_ids=i, fields="deactivated,city")[0]
        count += 1
        print(count)
        if "deactivated" in status:
            print("Удаляем ", status)
            vk.groups.removeUser(group_id=158787639, user_id=int(i))


def clear_banned_list():
    banned = vk.groups.getBanned(group_id=158787639)
    count_banned = banned['count']
    print("Всего забаненных в группе - ", count_banned)
    offset_banned = 200
    banned = banned['items']
    while offset_banned < count_banned:
        banned.extend(vk.groups.getBanned(group_id=158787639, count=200, offset=offset_banned)['items'])
        offset_banned += 200
    count = 0
    for i in banned:
        count += 1
        if "profile" not in i:
            print("Не юзер - ", i)
            continue
        status = vk.users.get(user_ids=i["profile"]["id"], fields="deactivated,city")[0]
        print(count, status)
        if "deactivated" in status:
            print("Удаляем ", status["id"])
            vk.groups.unban(group_id=158787639, user_id=status["id"])


# Подключаемся к ВК
session = config.session
vk_session = VkApi(token=session["VK_TOKEN_VALSTAN"])
vk = vk_session.get_api()

# del_delete_users()
clear_banned_list()
